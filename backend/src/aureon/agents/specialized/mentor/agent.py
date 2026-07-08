from aureon.agents.base import BaseAgent
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.mentor.matching import analyze_mentor_matches
from aureon.agents.specialized.mentor.schemas import MentorMatchTurnOutput
from aureon.agents.specialized.mentor.tools import (
    MentorProfileReaderTool,
    PublicationReaderTool,
    ResearchProfileReaderTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class MentorAgent(BaseAgent):
    """Recommends suitable experienced human professionals whenever the
    orchestrator determines human guidance would help.

    Owns mentor-matching outright: ``find_matches`` (below) is the real
    reasoning entry point, used by the direct API route
    (api/v1/decision.py) and reachable via delegation from Decision
    through the Mission Orchestrator — this logic used to live inside
    Decision's own module, which never should have owned it.

    Deliberately NOT recommendation-stage: human handoff must stay
    reachable at any confidence level — a confused student early in
    Exploration Mode may need a mentor most. Resolved handoffs are appended
    to the student's long-term profile (``StudentProfile.mentor_interactions``)
    so mentor guidance becomes part of the student's ongoing journey rather
    than a one-off event.
    """

    name = AgentName.MENTOR.value
    description = (
        "Recommends experienced human mentors and manages handoff when AI "
        "judges human guidance is beneficial; not gated by confidence."
    )

    async def find_matches(
        self,
        profile: StudentProfile,
        mentors: list[Mentor],
        *,
        llm: LLMClient,
        mission: Mission | None = None,
    ) -> MentorMatchTurnOutput:
        """Mentor Agent's own capability (Investigation + Knowledge
        Fusion). Records its real execution stages onto the mission, if
        one is supplied, at the two points that are genuinely distinct
        steps in this code today — before reasoning starts and after the
        profile is built — rather than fabricating timestamps for
        sub-steps the current single LLM call doesn't separately expose.
        """
        stages = AGENT_EXECUTION_STAGES[self.name]

        # Mentor's own investigation toolset — attempted every analysis
        # (honest not_connected today: no stored mentor profile/publication
        # URLs configured yet).
        tool_results = [await run_tool_safely(PublicationReaderTool())]
        if mission is not None:
            mission.record_stage(stages[0])  # "Reading Publications"
        tool_results.append(await run_tool_safely(ResearchProfileReaderTool()))
        if mission is not None:
            mission.record_stage(stages[1])  # "Comparing Expertise"
        tool_results.append(await run_tool_safely(MentorProfileReaderTool()))

        output = await analyze_mentor_matches(profile, mentors, llm=llm)
        if mission is not None:
            mission.record_stage(stages[2])  # "Matching Career DNA"
            mission.record_stage(stages[3])  # "Preparing Mentor Report"
            mission.artifacts.setdefault("tool_results", {})[self.name] = [
                r.model_dump() for r in tool_results
            ]
        return output

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough for the conversational graph loop —
        # mentor matching's primary trigger is the direct API route
        # ("conversation optional"), reached via find_matches() above.
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
