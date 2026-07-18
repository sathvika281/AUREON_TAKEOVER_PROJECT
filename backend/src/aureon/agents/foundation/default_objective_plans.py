"""Responsibility: register today's 3 real Build Orchestrator objectives.
Owns: the only calls to ``register_objective_plan`` for these 3
objectives. Does NOT own: the registry itself (``objective_registry.py``)
or any agent's reasoning. Consumed by: imported once for its side
effects from ``agents/foundation/__init__.py``.

Extension point — a future objective is added by writing its own
``register_objective_plan(...)`` call (in this file or, more naturally,
a new small module of its own once Phase 2 features exist) — this file
is never a growing switch statement inside Build Orchestrator itself.

Each objective mirrors an existing real route exactly (api/v1/decision.py,
api/v1/growth.py) — same objective string, same primary_agent, same
delegation shape — so Build Orchestrator's very first real behavior is
provably identical to what already works today.
"""

from datetime import datetime, timezone
from typing import Any

from aureon.agents.foundation.objective_registry import (
    ExecutionPlan,
    ExecutionStep,
    register_objective_plan,
)
from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.mission import Mission
from aureon.agents.registry import AgentRegistry
from aureon.agents.specialized.institution.matching import upsert_college_matches
from aureon.agents.specialized.mentor.matching import upsert_mentor_matches
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.shared.types import AgentName


async def _load_mentor_resources() -> dict[str, Any]:
    return {"mentors": await MentorRepository().list_mentors()}


async def _load_institution_resources() -> dict[str, Any]:
    return {"institutions": await InstitutionRepository().list_institutions()}


async def _mentor_call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
    """Mirrors api/v1/decision.py's analyze_mentor_matches_route exactly:
    find_matches, then persist real matches into profile.mentor_matches
    (skipped only when the agent itself reports insufficient evidence) —
    so Build Orchestrator's Career Memory Connections domain (derived
    from mentor_matches) reflects genuinely new state, not just a
    transient in-mission artifact."""
    agent = AgentRegistry.get(AgentName.MENTOR.value)
    output = await agent.find_matches(profile, resources["mentors"], llm=llm, mission=mission)
    if not output.insufficient_evidence:
        mentors_by_id = {m.id: m.name for m in resources["mentors"]}
        upsert_mentor_matches(profile, output.matches, mentors_by_id, datetime.now(timezone.utc))
    return output


async def _institution_call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
    """Mirrors api/v1/decision.py's analyze_college_matches_route exactly
    — see _mentor_call's docstring."""
    agent = AgentRegistry.get(AgentName.INSTITUTION.value)
    output = await agent.find_matches(profile, resources["institutions"], llm=llm, mission=mission)
    if not output.insufficient_evidence:
        institutions_by_id = {i.id: i.name for i in resources["institutions"]}
        upsert_college_matches(profile, output.matches, institutions_by_id, datetime.now(timezone.utc))
    return output


def _growth_call(profile: StudentProfile, llm: LLMClient, mission: Mission, resources: dict[str, Any]):
    agent = AgentRegistry.get(AgentName.GROWTH.value)
    return agent.build_report(profile, llm=llm, mission=mission)


register_objective_plan(
    "mentor_match_analysis",
    ExecutionPlan(
        primary_agent=AgentName.DECISION.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.MENTOR.value,
                capability=Capability.INVESTIGATION,
                build_call=_mentor_call,
            )
        ],
        reasoning="Decision Lab needs mentor-fit analysis, which Mentor Agent owns.",
        load_resources=_load_mentor_resources,
    ),
)

register_objective_plan(
    "college_match_analysis",
    ExecutionPlan(
        primary_agent=AgentName.DECISION.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.INSTITUTION.value,
                capability=Capability.INVESTIGATION,
                build_call=_institution_call,
            )
        ],
        reasoning="Decision Lab needs college-fit analysis, which Institution Agent owns.",
        load_resources=_load_institution_resources,
    ),
)

register_objective_plan(
    "progress_intelligence_analysis",
    ExecutionPlan(
        primary_agent=AgentName.GROWTH.value,
        steps=[
            ExecutionStep(
                agent_name=AgentName.GROWTH.value,
                capability=None,  # primary agent doing its own work — no delegation
                build_call=_growth_call,
            )
        ],
        reasoning="Growth is both primary and only specialist — Progress Intelligence is entirely its own capability.",
    ),
)

# No entry for Discovery — extension point: Discovery's only real trigger
# today is the conversational graph, not a Mission-callable method the
# way Institution/Mentor/Growth each gained one. When: once a future
# objective genuinely needs identity reasoning outside conversation.
# Who: whichever future feature needs it.
