from datetime import datetime, timezone

from langchain_core.messages import AIMessage

from aureon.agents.base import BaseAgent
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.career_intelligence.candidates import upsert_candidates
from aureon.agents.specialized.career_intelligence.reasoning import analyze_careers
from aureon.agents.specialized.career_intelligence.tools import (
    BrowserInvestigationTool,
    SearchTool,
    TrendInvestigationTool,
    URLReaderTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.shared.types import AgentName


class CareerIntelligenceAgent(BaseAgent):
    """Reasons about which real careers from the Career Knowledge Base
    might fit this student, grounded in Career DNA, the Evidence Graph,
    and Discovery's hypotheses — never LLM memory alone. Recommendation
    stage: gated by the confidence safety floor when reached
    conversationally (see agents/confidence_gate.py); the dedicated
    analyze API route (api/v1/career_intelligence.py) is the primary
    trigger and applies its own, separate evidence floor since it isn't
    conversational turn-taking.
    """

    name = AgentName.CAREER_INTELLIGENCE.value
    description = (
        "Reasons about which real careers from the Career Knowledge Base fit this "
        "student's Career DNA and evidence; explains matches with supporting/"
        "contradicting/missing evidence; never recommends without evidence."
    )
    is_recommendation_stage = True

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        stages = AGENT_EXECUTION_STAGES[self.name]
        profile = state["student_profile"] or StudentProfile(student_id=state["student_id"])
        executed_stages = [stages[0]]  # "Mission Planned"

        # Career Intelligence's own investigation toolset — attempted every
        # analysis (honest not_connected today: no search API key, no
        # browser/fetch backend configured yet).
        tool_results = [
            await run_tool_safely(SearchTool()),
            await run_tool_safely(BrowserInvestigationTool()),
        ]
        executed_stages.append(stages[1])  # "Searching Sources"
        tool_results.append(await run_tool_safely(URLReaderTool()))
        executed_stages.append(stages[2])  # "Reading Web Pages"

        careers = await CareerRepository().list_careers()
        output = await analyze_careers(profile, careers, llm=llm)
        executed_stages.append(stages[3])  # "Comparing Findings"

        tool_results.append(await run_tool_safely(TrendInvestigationTool()))
        executed_stages.append(stages[4])  # "Cross-Verifying Information"

        now = datetime.now(timezone.utc)
        if not output.insufficient_evidence:
            # Always runs even when `candidates` is empty this round — an
            # analysis that genuinely finds no fits must still discard any
            # previously-active candidates it no longer surfaces, not just
            # skip the step silently.
            careers_by_id = {c.id: c.name for c in careers}
            executed_stages.append(stages[5])  # "Knowledge Fusion" (Career DNA + evidence + candidates merged)
            upsert_candidates(profile, output.candidates, careers_by_id, now)

        executed_stages.append(stages[6])  # "Preparing Investigation Report"
        state["agent_outputs"][self.name] = AgentOutput(
            agent_name=self.name,
            payload={
                "candidates": [c.model_dump() for c in output.candidates],
                "insufficient_evidence": output.insufficient_evidence,
                "insufficient_evidence_reason": output.insufficient_evidence_reason,
                "execution_stages": executed_stages,
                "tool_results": [r.model_dump() for r in tool_results],
            },
        )
        state["messages"] = [AIMessage(content=output.reply_to_student)]
        profile.updated_at = now
        state["student_profile"] = profile
        state["agent_history"].append(self.name)
        return state
