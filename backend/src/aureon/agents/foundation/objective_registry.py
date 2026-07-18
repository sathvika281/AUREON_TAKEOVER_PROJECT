"""Responsibility: the registration mechanism for "which agents does a
Build Orchestrator objective run, and in what order." Owns: the
objective -> ``ExecutionPlan`` mapping (module-private dict) and the
``ExecutionStep``/``ExecutionPlan`` shapes. Does NOT own: which
objectives are actually registered — that lives in
``default_objective_plans.py`` — nor any agent's own reasoning, which
stays inside that agent's own module. Consumed by:
``CareerOrchestratorAgent.plan_execution`` (read) and
``default_objective_plans.py`` (write, at import time).

Extension point — to add a future objective, call
``register_objective_plan(...)`` from your own module; nothing here or
in ``build_orchestrator.py`` needs to change.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.mission import Mission
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient


@dataclass(frozen=True)
class ExecutionStep:
    """One agent's real participation in an objective. ``capability`` is
    ``None`` only when ``agent_name`` is the plan's own ``primary_agent``
    (it does the work directly, no delegation is needed) — otherwise it
    must be a capability the target agent owns (enforced by
    ``MissionOrchestrator.delegate``)."""

    agent_name: str
    capability: Capability | None
    #: Given the loaded profile, the LLM client, the in-flight Mission,
    #: and whatever ``ExecutionPlan.load_resources`` produced, return the
    #: awaitable that performs this agent's real work — exactly the
    #: ``call=lambda: ...`` already used by every existing mission-backed
    #: route (see api/v1/decision.py, api/v1/growth.py).
    build_call: Callable[[StudentProfile, LLMClient, Mission, dict[str, Any]], Awaitable[Any]]


@dataclass(frozen=True)
class ExecutionPlan:
    """A deterministic, registered recipe for one Build Orchestrator
    objective. ``primary_agent`` matches the same field every existing
    mission-backed route already passes to
    ``MissionOrchestrator.create_mission`` — the agent framed as "asking"
    for the work, whether or not it also appears in ``steps``."""

    primary_agent: str
    steps: list[ExecutionStep]
    reasoning: str
    #: Optional async loader for resources a step's ``build_call`` needs
    #: beyond the profile/llm/mission (e.g. the real mentor/institution
    #: list from their own knowledge-base repositories). Runs once before
    #: any step executes.
    load_resources: Callable[[], Awaitable[dict[str, Any]]] | None = None


_PLANS: dict[str, ExecutionPlan] = {}


def register_objective_plan(objective: str, plan: ExecutionPlan) -> None:
    _PLANS[objective] = plan


def get_objective_plan(objective: str) -> ExecutionPlan:
    if objective not in _PLANS:
        raise ValueError(f"No execution plan registered for objective '{objective}'")
    return _PLANS[objective]
