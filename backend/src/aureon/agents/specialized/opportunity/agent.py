from aureon.agents.base import BaseAgent
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.opportunity.tools import (
    CompetitionSearchTool,
    InternshipSearchTool,
    OpportunitySearchTool,
    ResearchOpportunitySearchTool,
)
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class OpportunityAgent(BaseAgent):
    """Surfaces internships, scholarships, competitions, research
    programs, and jobs connected to the student's Career DNA (Stage 4:
    Build Your Journey — Opportunity Graph).

    Honest no-op stub, same shape as every other not-yet-built specialist
    (Growth, Roadmap, Skill Gap were stubs before this task; Mentor and
    Institution just graduated out of stub status by gaining
    ``find_matches``). No real opportunity data source exists yet — this
    agent registers a real identity and capability ownership (Investigation
    + Trend Monitoring) so a later phase can implement it without any
    architectural change here, rather than never having existed at all.
    """

    name = AgentName.OPPORTUNITY.value
    description = (
        "Surfaces internships, scholarships, competitions, research programs, and jobs "
        "connected to the student's Career DNA."
    )

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Opportunity-matching logic doesn't exist yet, but its toolset is
        # real and attempted honestly (all not_connected today) — a later
        # phase gives these a real data source without any architecture
        # change here.
        stages = AGENT_EXECUTION_STAGES[self.name]
        tool_results = [
            await run_tool_safely(OpportunitySearchTool()),
            await run_tool_safely(InternshipSearchTool()),
            await run_tool_safely(ResearchOpportunitySearchTool()),
            await run_tool_safely(CompetitionSearchTool()),
        ]
        executed_stages = list(stages)  # every stage genuinely attempted, none skipped

        state["agent_outputs"][self.name] = AgentOutput(
            agent_name=self.name,
            payload={
                "execution_stages": executed_stages,
                "tool_results": [r.model_dump() for r in tool_results],
            },
        )
        state["agent_history"].append(self.name)
        return state
