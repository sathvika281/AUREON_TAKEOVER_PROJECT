from datetime import datetime, timezone

from langchain_core.messages import AIMessage

from aureon.agents.base import BaseAgent
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.decision.reasoning import analyze_comparison, finalize_comparison
from aureon.agents.state import AureonState
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.career_exploration import record_exploration_event
from aureon.domain.services.decision_memory import record_comparison_memory
from aureon.services.llm.base import LLMClient
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.shared.types import AgentName

#: The conversational path needs at least this many active career
#: candidates before a comparison is meaningful — comparing careers the
#: student hasn't even been matched to yet would be exactly the generic
#: comparison this product refuses to produce. The direct API routes
#: (the primary trigger — "conversation optional") apply their own,
#: identical floor independently.
MIN_CANDIDATES_FOR_COMPARISON = 2

#: Comparing more than this within one conversational reply gets noisy;
#: the direct Decision Lab UI lets a student pick exactly which ones.
MAX_CANDIDATES_FOR_CONVERSATIONAL_COMPARISON = 3


class DecisionAgent(BaseAgent):
    """Aureon's decision-support agent: compares careers, explains
    trade-offs and uncertainty, matches mentors, matches institutions —
    all grounded in Career DNA/Evidence Graph/Career Candidates, never a
    recommendation or a ranking. The primary trigger for every one of
    these is a direct API route (api/v1/decision.py, api/v1/mentors.py,
    api/v1/institutions.py), since "conversation optional" is the
    product's stated UX — this conversational path exists so the agent
    is still genuinely reachable if the planner routes here, and defaults
    to comparing the student's current top career candidates (the most
    central "decide" behavior) rather than requiring a separate
    conversational intent-classification step.
    """

    name = AgentName.DECISION.value
    description = (
        "Supports decision-making: compares careers, explains trade-offs and uncertainty, "
        "matches mentors and institutions — grounded in Career DNA and evidence, never a "
        "recommendation or a ranking."
    )
    is_recommendation_stage = True

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        stages = AGENT_EXECUTION_STAGES[self.name]
        profile = state["student_profile"] or StudentProfile(student_id=state["student_id"])
        active_candidates = [c for c in profile.career_candidates if c.status != "discarded"]
        executed_stages = [stages[0]]  # "Reviewing Candidate Careers"

        if len(active_candidates) < MIN_CANDIDATES_FOR_COMPARISON:
            reply = (
                "I don't have enough career candidates to compare yet — keep exploring in "
                "Career Intelligence first, and I can compare options once there are at least "
                "two worth weighing against each other."
            )
            state["agent_outputs"][self.name] = AgentOutput(
                agent_name=self.name,
                payload={"insufficient_evidence": True, "execution_stages": executed_stages},
            )
            state["messages"] = [AIMessage(content=reply)]
            state["agent_history"].append(self.name)
            return state

        top_candidates = sorted(active_candidates, key=lambda c: c.confidence, reverse=True)[
            :MAX_CANDIDATES_FOR_CONVERSATIONAL_COMPARISON
        ]
        career_ids = [c.career_id for c in top_candidates]
        careers = [c for c in await CareerRepository().list_careers() if c.id in career_ids]

        output = await analyze_comparison(profile, careers, llm=llm)
        executed_stages.append(stages[1])  # "Comparing Trade-offs"
        now = datetime.now(timezone.utc)

        comparison = finalize_comparison(career_ids, careers, output, now)
        profile.career_comparisons.append(comparison)
        record_comparison_memory(profile, comparison, now)
        for cid in career_ids:
            record_exploration_event(
                profile, career_id=cid, interaction_type="compared",
                metadata={"compared_with": [other for other in career_ids if other != cid]}, now=now,
            )

        executed_stages.append(stages[3])  # "Building Decision Report" (no delegation on this path)
        state["agent_outputs"][self.name] = AgentOutput(
            agent_name=self.name,
            payload={"comparison_id": comparison.id, "execution_stages": executed_stages},
        )
        state["messages"] = [AIMessage(content=output.reply_to_student)]
        profile.updated_at = now
        state["student_profile"] = profile
        state["agent_history"].append(self.name)
        return state
