from aureon.agents.base import BaseAgent
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.institution.matching import analyze_college_matches
from aureon.agents.specialized.institution.schemas import CollegeMatchTurnOutput
from aureon.agents.specialized.institution.tools import (
    AdmissionPDFReaderTool,
    CurriculumReaderTool,
    ResearchLabReaderTool,
    UniversityWebsiteReaderTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.institution import Institution
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class InstitutionAgent(BaseAgent):
    """Recommends colleges, universities, bootcamps, research institutions
    and learning ecosystems suited to the student.

    Owns college-matching outright: ``find_matches`` (below) is the real
    reasoning entry point, used by the direct API route
    (api/v1/decision.py) and reachable via delegation from Decision
    through the Mission Orchestrator — this logic used to live inside
    Decision's own module, which never should have owned it.
    """

    name = AgentName.INSTITUTION.value
    description = (
        "Recommends colleges, universities, bootcamps, research "
        "institutions, and learning ecosystems."
    )

    async def find_matches(
        self,
        profile: StudentProfile,
        institutions: list[Institution],
        *,
        llm: LLMClient,
        mission: Mission | None = None,
    ) -> CollegeMatchTurnOutput:
        """Institution Agent's own capability (Investigation + Document
        Intelligence). Records its real execution stages onto the
        mission, if one is supplied, at the two points that are genuinely
        distinct steps in this code today."""
        stages = AGENT_EXECUTION_STAGES[self.name]

        # Institution's own investigation toolset — attempted every
        # analysis (honest not_connected today: no stored institution
        # URLs, no PDF library configured yet).
        tool_results = [
            await run_tool_safely(CurriculumReaderTool()),
        ]
        if mission is not None:
            mission.record_stage(stages[0])  # "Reading Curriculum"
        tool_results.append(await run_tool_safely(ResearchLabReaderTool()))
        if mission is not None:
            mission.record_stage(stages[1])  # "Reviewing Research Labs"
        tool_results.append(await run_tool_safely(UniversityWebsiteReaderTool()))
        tool_results.append(await run_tool_safely(AdmissionPDFReaderTool()))

        output = await analyze_college_matches(profile, institutions, llm=llm)
        if mission is not None:
            mission.record_stage(stages[2])  # "Comparing Institutions"
            mission.record_stage(stages[3])  # "Building Institution Profile"
            mission.artifacts.setdefault("tool_results", {})[self.name] = [
                r.model_dump() for r in tool_results
            ]
        return output

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough for the conversational graph loop —
        # college matching's primary trigger is the direct API route
        # ("conversation optional"), reached via find_matches() above.
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
