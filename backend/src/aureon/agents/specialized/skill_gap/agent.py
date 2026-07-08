from aureon.agents.base import BaseAgent
from aureon.agents.state import AureonState
from aureon.domain.models.agent_output import AgentOutput
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class SkillGapAgent(BaseAgent):
    """Compares current skills against required skills for a target career
    and identifies the gap, generating personalized improvement
    suggestions."""

    name = AgentName.SKILL_GAP.value
    description = (
        "Compares current skills to required skills, identifies missing "
        "skills, and generates personalized improvement suggestions."
    )

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough — skill-gap analysis logic is
        # implemented in this agent's dedicated module, not this scaffold.
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
