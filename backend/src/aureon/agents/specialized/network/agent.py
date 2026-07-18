"""Responsibility: registration placeholder for a future Network domain
(mentors, networking, expert recommendations). Owns: nothing yet — no
capability entry in agents/mission/capabilities.py, no extra method, no
tool calls. Does NOT own: Mentor+Institution's real matching, which
stays exactly where it is (agents/specialized/mentor,
agents/specialized/institution) — this agent is a future facade over
that matching, not a replacement for it. Consumed by: nothing yet.

Extension point — why: registered per architecture decision so a future
feature can integrate cleanly without a schema/registry change later;
when: once a Phase 2 feature needs a real Network workflow; who: that
future feature.
"""

from aureon.agents.base import BaseAgent
from aureon.agents.state import AureonState
from aureon.domain.models.agent_output import AgentOutput
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class NetworkAgent(BaseAgent):
    name = AgentName.NETWORK.value
    description = (
        "Placeholder for a future facade over mentor and institution matching, "
        "networking, and expert recommendations. No real workflow yet."
    )
    is_recommendation_stage = False

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
