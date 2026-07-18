"""Responsibility: Exposure Universe's unified composition layer for the
merged "Missing Worlds + Exposure Universe" frontend screen. Owns:
``build_exposure_universe``, ``build_world_detail``. Does NOT own
exploration-level detection (``missing_worlds_engine.py``, called
verbatim) or unfamiliar-career selection (``exposure_recommendation.py``,
called verbatim) — this file only groups, labels, and cross-links their
real outputs; it never re-derives either engine's intelligence. Consumed
by: ``api/v1/exposure.py``.
"""

from dataclasses import dataclass
from datetime import datetime

from aureon.domain.models.career import Career, CareerStory
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.experiment import Experiment
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_history import get_completed_experiment_ids
from aureon.domain.services.exposure_recommendation import (
    ExposureEnrichment,
    build_exposure_enrichment,
    curiosity_hook_for,
    get_exposure_suggestions,
)
from aureon.domain.services.missing_worlds_engine import (
    WorldExploration,
    analyze_missing_worlds,
)
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.journey_story_repository import JourneyStoryRepository

MAX_RELATED_CAREERS = 5
MAX_RELATED_STORIES = 3
MAX_RELATED_EXPERTS = 3


@dataclass(frozen=True)
class WorldExposureSummary:
    world_name: str
    level: str


@dataclass(frozen=True)
class ExposureMap:
    engaged: list[WorldExposureSummary]
    limited_or_none: list[WorldExposureSummary]


@dataclass(frozen=True)
class MissingWorldCard:
    world: CareerWorld
    level: str
    match_count: int
    why_missing: str
    related_careers: list[Career]
    linked_circle: KnowledgeCircle | None


@dataclass(frozen=True)
class ExposurePossibility:
    career: Career
    enrichment: ExposureEnrichment
    curiosity_hook: str
    related_missing_world: str | None


@dataclass(frozen=True)
class ExposureUniverse:
    exposure_map: ExposureMap
    missing_worlds: list[MissingWorldCard]
    possibilities: list[ExposurePossibility]


@dataclass(frozen=True)
class WorldExplorationDetail:
    world: CareerWorld
    level: str
    match_count: int
    why_missing: str
    related_careers: list[Career]
    related_stories: list[CareerStory]
    related_experts: list[Mentor]
    linked_circle: KnowledgeCircle | None


def _world_industries(world: CareerWorld) -> set[str]:
    return {i.lower() for i in world.related_industries}


def _careers_for_world(
    world: CareerWorld, careers: list[Career], *, limit: int = MAX_RELATED_CAREERS
) -> list[Career]:
    """A deterministic membership join against `related_industries` — the
    exact vocabulary `missing_worlds_engine.py` already trusts to decide
    exploration, not an invented matching rule. Falls back to
    case-insensitive substring overlap against the world's own name only
    when a world has no `related_industries` at all."""
    industries = _world_industries(world)
    if industries:
        matches = [c for c in careers if c.industry.lower() in industries]
    else:
        name = world.name.lower()
        matches = [
            c
            for c in careers
            if name in c.industry.lower()
            or c.industry.lower() in name
            or any(name in tag.lower() or tag.lower() in name for tag in c.trait_tags)
        ]
    return matches[:limit]


def _explain_why_missing(world: CareerWorld, explorations: list[WorldExploration]) -> str:
    """Grounded in the student's OWN real exploration data — never a
    generic template. Cites their most-explored world(s) by name when any
    exist; a graceful, still-honest fallback otherwise."""
    engaged = sorted(
        (e for e in explorations if e.level != "unexplored" and e.world.id != world.id),
        key=lambda e: -e.match_count,
    )
    if engaged:
        top_names = [e.world.name for e in engaged[:2]]
        joined = " and ".join(top_names)
        return (
            f"You've spent real time exploring {joined}, but Aureon has found little to no "
            f"evidence that you've meaningfully encountered {world.name} yet."
        )
    return f"Aureon hasn't found evidence yet that you've encountered {world.name}."


def _linked_circle(world: CareerWorld, knowledge_circles: list[KnowledgeCircle]) -> KnowledgeCircle | None:
    return next((c for c in knowledge_circles if c.linked_career_world_id == world.id), None)


def _related_missing_world_name(career: Career, recommended_next: list[CareerWorld]) -> str | None:
    industry = career.industry.lower()
    for world in recommended_next:
        if industry in _world_industries(world):
            return world.name
    return None


def build_exposure_universe(
    *,
    profile: StudentProfile,
    worlds: list[CareerWorld],
    careers: list[Career],
    experiments: list[Experiment],
    knowledge_circles: list[KnowledgeCircle],
    now: datetime,
) -> ExposureUniverse:
    """Mutates `profile.exposure_history` (via `get_exposure_suggestions`,
    called verbatim below) — same contract as the pre-merge route: the
    caller persists `profile` after this returns."""
    analysis = analyze_missing_worlds(profile, worlds, careers)
    explorations_by_world_id = {e.world.id: e for e in analysis.explorations}

    engaged_explorations = sorted(
        (e for e in analysis.explorations if e.level != "unexplored"), key=lambda e: -e.match_count
    )
    exposure_map = ExposureMap(
        engaged=[WorldExposureSummary(world_name=e.world.name, level=e.level) for e in engaged_explorations],
        limited_or_none=[
            WorldExposureSummary(world_name=e.world.name, level=e.level)
            for e in analysis.explorations
            if e.level == "unexplored"
        ],
    )

    missing_worlds = [
        MissingWorldCard(
            world=world,
            level=explorations_by_world_id[world.id].level,
            match_count=explorations_by_world_id[world.id].match_count,
            why_missing=_explain_why_missing(world, analysis.explorations),
            related_careers=_careers_for_world(world, careers),
            linked_circle=_linked_circle(world, knowledge_circles),
        )
        for world in analysis.recommended_next
    ]

    completed_ids = get_completed_experiment_ids(profile)
    selected = get_exposure_suggestions(profile, careers, now=now)
    possibilities = [
        ExposurePossibility(
            career=career,
            enrichment=build_exposure_enrichment(career, experiment_catalog=experiments, completed_ids=completed_ids),
            curiosity_hook=curiosity_hook_for(career),
            related_missing_world=_related_missing_world_name(career, analysis.recommended_next),
        )
        for career in selected
    ]

    return ExposureUniverse(exposure_map=exposure_map, missing_worlds=missing_worlds, possibilities=possibilities)


async def build_world_detail(
    *,
    world_id: str,
    profile: StudentProfile,
    worlds: list[CareerWorld],
    careers: list[Career],
    knowledge_circles: list[KnowledgeCircle],
    stories: JourneyStoryRepository,
    experts: ExpertRepository,
) -> WorldExplorationDetail | None:
    world = next((w for w in worlds if w.id == world_id), None)
    if world is None:
        return None

    analysis = analyze_missing_worlds(profile, worlds, careers)
    exploration = next(e for e in analysis.explorations if e.world.id == world_id)
    related_careers = _careers_for_world(world, careers)

    related_stories: list[CareerStory] = []
    for career in related_careers[:3]:
        found, _total = await stories.search_stories(career_id=career.id, limit=MAX_RELATED_STORIES)
        related_stories.extend(found)
        if len(related_stories) >= MAX_RELATED_STORIES:
            break
    related_stories = related_stories[:MAX_RELATED_STORIES]

    related_experts: list[Mentor] = []
    seen_expert_ids: set[str] = set()
    for career in related_careers[:2]:
        found, _total = await experts.search_experts(industry=career.industry, limit=MAX_RELATED_EXPERTS)
        for expert in found:
            if expert.id not in seen_expert_ids:
                related_experts.append(expert)
                seen_expert_ids.add(expert.id)
        if len(related_experts) >= MAX_RELATED_EXPERTS:
            break
    related_experts = related_experts[:MAX_RELATED_EXPERTS]

    return WorldExplorationDetail(
        world=world,
        level=exploration.level,
        match_count=exploration.match_count,
        why_missing=_explain_why_missing(world, analysis.explorations),
        related_careers=related_careers,
        related_stories=related_stories,
        related_experts=related_experts,
        linked_circle=_linked_circle(world, knowledge_circles),
    )
