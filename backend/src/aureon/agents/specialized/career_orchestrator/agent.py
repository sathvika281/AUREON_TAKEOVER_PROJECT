"""Responsibility: resolve a Build Orchestrator objective into the
ordered list of agents that will actually execute it. Owns:
``plan_execution`` — a thin wrapper over the registered
``objective_registry`` (agents/foundation/objective_registry.py), never
its own hardcoded mapping. Does NOT own: any specialist's own reasoning,
Mission coordination mechanics (MissionOrchestrator, untouched), or
Career Memory/Event/Universe/Journey Guidance logic. Consumed by:
``BuildOrchestrator`` only — its ``run()`` is a no-op passthrough for
the conversational graph, since this agent's real trigger is Build
Orchestrator, not conversation.
"""

from aureon.agents.base import BaseAgent
from aureon.agents.foundation.objective_registry import ExecutionPlan, get_objective_plan
from aureon.agents.state import AureonState
from aureon.domain.models.agent_output import AgentOutput
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName


class CareerOrchestratorAgent(BaseAgent):
    name = AgentName.CAREER_ORCHESTRATOR.value
    description = (
        "Coordinates which specialists a Phase 2 request needs and in what order; "
        "the platform's single coordination brain, called by BuildOrchestrator."
    )
    is_recommendation_stage = False

    def plan_execution(self, *, objective: str, profile: StudentProfile) -> ExecutionPlan:
        """Real coordination logic (not a stub) — resolves via the
        registry rather than owning a mapping itself, so a new objective
        never requires editing this method. ``profile`` is accepted (not
        yet used) so a future planner can make profile-aware decisions
        (e.g. picking between two plans for the same objective) without
        changing this method's signature."""
        return get_objective_plan(objective)

    async def run(self, state: AureonState, *, llm: LLMClient) -> AureonState:
        # Honest no-op passthrough for the conversational graph — this
        # agent's real trigger is BuildOrchestrator.handle_request, not
        # the LangGraph loop.
        state["agent_outputs"][self.name] = AgentOutput(agent_name=self.name)
        state["agent_history"].append(self.name)
        return state
