"""Responsibility: register Opportunity Hub's 7 real Build Orchestrator
objectives (Phase 2 Stage 2). Owns: the only calls to
``register_objective_plan``/``register_objective_event`` for these 7
objectives. Does NOT own: the registries themselves or
``OpportunityAgent``'s own reasoning. Consumed by: imported once for
its side effects from ``agents/foundation/__init__.py``.

Also imports ``agents.specialized.opportunity.providers`` for its
registration side effect (the seeded Knowledge Base provider) — nothing
else in this foundation currently triggers that import.

The 5 interaction objectives (viewed/saved/applied/withdrawn/completed)
each look up the real ``Opportunity`` by ``context["opportunity_id"]``
through the same provider aggregation Discovery/Fit-Evaluation use, so
Career Memory's ``OpportunityEntry`` always records the opportunity's
real, current ``category``/``title``/``version`` — never data supplied
blindly by a caller.
"""

from datetime import datetime, timezone
from typing import Any, Literal

from aureon.agents.foundation.objective_registry import (
    ExecutionPlan,
    ExecutionStep,
    register_objective_plan,
)
from aureon.agents.mission.mission import Mission
from aureon.agents.registry import AgentRegistry
from aureon.agents.specialized.opportunity import providers  # noqa: F401 — registers the seeded provider
from aureon.agents.specialized.opportunity.filtering import OpportunityFilters
from aureon.agents.specialized.opportunity.providers.registry import fetch_all_safely
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.foundation.career_memory.service import record_opportunity_entry
from aureon.services.foundation.events.objective_event_registry import register_objective_event
from aureon.services.foundation.events.types import EventType
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName

InteractionKind = Literal["viewed", "saved", "applied", "withdrawn", "completed"]


async def _load_opportunity_catalog() -> dict[str, Any]:
    return {"opportunities": await fetch_all_safely()}


async def _opportunity_discovery_call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
    agent = AgentRegistry.get(AgentName.OPPORTUNITY.value)
    filters: OpportunityFilters | None = resources.get("filters")
    query: str | None = resources.get("query")
    top_n: int = resources.get("top_n", 5)
    return await agent.find_opportunities(
        profile, resources["opportunities"], filters=filters, query=query, llm=llm, mission=mission, top_n=top_n
    )


async def _opportunity_fit_evaluation_call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
    agent = AgentRegistry.get(AgentName.OPPORTUNITY.value)
    opportunity = await _find_opportunity(resources["opportunity_id"])
    return await agent.evaluate_fit(profile, opportunity, mission=mission)


async def _find_opportunity(opportunity_id: str):
    opportunities = await fetch_all_safely()
    opportunity = next((o for o in opportunities if o.id == opportunity_id), None)
    if opportunity is None:
        raise ValueError(f"Unknown opportunity_id: {opportunity_id}")
    return opportunity


def _make_interaction_call(interaction: InteractionKind):
    async def _call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
        opportunity = await _find_opportunity(resources["opportunity_id"])
        return record_opportunity_entry(
            profile,
            interaction=interaction,
            category=opportunity.category,
            ref_id=opportunity.id,
            opportunity_version=opportunity.version,
            title=opportunity.title,
            now=datetime.now(timezone.utc),
        )

    return _call


register_objective_plan(
    "opportunity_discovery",
    ExecutionPlan(
        primary_agent=AgentName.OPPORTUNITY.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.OPPORTUNITY.value,
                capability=None,  # primary agent doing its own work — no delegation
                build_call=_opportunity_discovery_call,
            )
        ],
        reasoning="Opportunity discovery/ranking is entirely Opportunity Agent's own capability.",
        load_resources=_load_opportunity_catalog,
    ),
)

register_objective_plan(
    "opportunity_fit_evaluation",
    ExecutionPlan(
        primary_agent=AgentName.OPPORTUNITY.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.OPPORTUNITY.value,
                capability=None,
                build_call=_opportunity_fit_evaluation_call,
            )
        ],
        reasoning="Single-opportunity fit evaluation is entirely Opportunity Agent's own capability.",
    ),
)

_INTERACTION_OBJECTIVES: list[tuple[str, InteractionKind, EventType]] = [
    ("opportunity_viewed", "viewed", EventType.OPPORTUNITY_VIEWED),
    ("opportunity_saved", "saved", EventType.OPPORTUNITY_SAVED),
    ("opportunity_applied", "applied", EventType.OPPORTUNITY_APPLIED),
    ("opportunity_withdrawn", "withdrawn", EventType.APPLICATION_WITHDRAWN),
    ("opportunity_completed", "completed", EventType.OPPORTUNITY_COMPLETED),
]

for _objective, _interaction, _event_type in _INTERACTION_OBJECTIVES:
    register_objective_plan(
        _objective,
        ExecutionPlan(
            primary_agent=AgentName.OPPORTUNITY.value,
            steps=[
                ExecutionStep(
                    agent_name=AgentName.OPPORTUNITY.value,
                    capability=None,
                    build_call=_make_interaction_call(_interaction),
                )
            ],
            reasoning=f"Recording a real '{_interaction}' interaction is Opportunity Agent's own capability.",
        ),
    )
    register_objective_event(_objective, _event_type)
