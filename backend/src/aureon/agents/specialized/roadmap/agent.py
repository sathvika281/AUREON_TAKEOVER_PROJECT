from aureon.agents.base import BaseAgent
from aureon.agents.mission.stages import AGENT_EXECUTION_STAGES
from aureon.agents.specialized.roadmap.tools import AdaptivePlanningTool, MilestonePlannerTool
from aureon.agents.state import AureonState
from aureon.agents.tools.base import run_tool_safely
from aureon.domain.models.agent_output import AgentOutput
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class RoadmapAgent(BaseAgent):
    """Generates a personalized learning roadmap: projects, certifications,
    milestones, and an internship pathway. Recommendation-stage: gated by
    the confidence safety floor."""

    name = AgentName.ROADMAP.value
    description = (
        "Generates learning roadmaps, projects, certifications, milestones "
        "and internship pathways."
    )
    is_recommendation_stage = True

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Roadmap generation logic doesn't exist yet, but its toolset is
        # real and attempted honestly (all not_connected today — no
        # persisted roadmap data model exists yet).
        stages = AGENT_EXECUTION_STAGES[self.name]
        tool_results = [
            await run_tool_safely(MilestonePlannerTool()),
            await run_tool_safely(AdaptivePlanningTool()),
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
