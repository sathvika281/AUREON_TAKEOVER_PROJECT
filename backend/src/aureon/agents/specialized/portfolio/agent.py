"""Responsibility: registration placeholder for a future Portfolio
domain (portfolio analysis, evidence extraction, project intelligence).
Owns: nothing yet — no capability entry in
agents/mission/capabilities.py, no extra method, no tool calls. Does
NOT own: GitHub/Document Intelligence's real extraction pipelines
(agents/document_intelligence/, agents/specialized/discovery/github_*),
which stay exactly where they are — this agent is a future facade over
evidence/project intelligence, not a replacement for those pipelines.
Consumed by: nothing yet.

Extension point — why: registered per architecture decision so a future
feature can integrate cleanly without a schema/registry change later;
when: once a Phase 2 feature needs a real Portfolio workflow; who: that
future feature.
"""

from aureon.agents.base import BaseAgent
from aureon.agents.state import AureonState
from aureon.domain.models.agent_output import AgentOutput
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class PortfolioAgent(BaseAgent):
    name = AgentName.PORTFOLIO.value
    description = (
        "Placeholder for a future portfolio analysis, evidence extraction, and "
        "project intelligence facade. No real workflow yet."
    )
    is_recommendation_stage = False

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
