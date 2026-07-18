"""Responsibility: Exposure Universe's orchestration layer — calls the
Exposure Engine, supplies real framing copy, and records history. Owns:
``get_exposure_suggestions``, ``curiosity_hook_for``,
``record_exposure_interaction``, ``build_exposure_enrichment``. Does
NOT own: candidate selection (``exposure_engine.py``) or the suggested-
activity match (``experiment_matching.py``, reused verbatim, not
re-derived — the same "one implementation only" precedent Hidden
Potential established). Consumed by: ``api/v1/exposure.py``.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from aureon.domain.models.career import Career
from aureon.domain.models.experiment import Experiment
from aureon.domain.models.exposure import ExposureHistoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_matching import suggest_activity
from aureon.domain.services.exposure_engine import select_exposure_careers

_FALLBACK_HOOK = "Discover something new — this is a world you haven't explored yet."

#: Kept small and honest — never a wall of links.
MAX_ITEMS_PER_SECTION = 2


def curiosity_hook_for(career: Career) -> str:
    """Real, seeded framing when available; an honest generic fallback
    (never an invented specific claim) otherwise."""
    return career.curiosity_hook or _FALLBACK_HOOK


@dataclass(frozen=True)
class ExposureEnrichment:
    mini_introduction: str
    quick_project: str | None
    watch: list[str] = field(default_factory=list)
    read: list[str] = field(default_factory=list)
    build: list[str] = field(default_factory=list)
    join: list[str] = field(default_factory=list)
    reflect_prompt: str = ""
    suggested_experience: Experiment | None = None


def build_exposure_enrichment(
    career: Career, *, experiment_catalog: list[Experiment], completed_ids: set[str]
) -> ExposureEnrichment:
    """Composes the richer Exposure Universe card content entirely from
    the (already-enriched) Career catalog — no separate catalog of its
    own. `build` merges real projects with open-source projects since
    both answer the same "try making something" question."""
    build_items = [*career.projects, *career.open_source_projects][:MAX_ITEMS_PER_SECTION]
    return ExposureEnrichment(
        mini_introduction=career.description,
        quick_project=career.projects[0] if career.projects else None,
        watch=career.videos[:MAX_ITEMS_PER_SECTION],
        read=career.books[:MAX_ITEMS_PER_SECTION],
        build=build_items,
        join=career.communities[:MAX_ITEMS_PER_SECTION],
        reflect_prompt=f"What part of being a {career.name} would you want to try first?",
        suggested_experience=suggest_activity(career.name, experiment_catalog, completed_ids),
    )


def get_exposure_suggestions(
    profile: StudentProfile, catalog: list[Career], *, now: datetime, limit: int = 3
) -> list[Career]:
    """Selects real unfamiliar careers and records them as `shown` in
    the same call — mutates `profile` in place; the caller persists."""
    selected = select_exposure_careers(catalog, profile, limit=limit)
    for career in selected:
        profile.exposure_history.append(
            ExposureHistoryEntry(id=str(uuid.uuid4()), career_id=career.id, shown_at=now, interaction="shown")
        )
    return selected


def record_exposure_interaction(
    profile: StudentProfile, *, career_id: str, interaction: str, now: datetime
) -> None:
    """Updates the real entry for this career if one exists (from being
    shown), otherwise appends a new one — either way, this career's
    latest real interaction state is what future selection/no-repeat
    logic reads."""
    for entry in profile.exposure_history:
        if entry.career_id == career_id:
            entry.interaction = interaction  # type: ignore[assignment]
            entry.shown_at = now
            return
    profile.exposure_history.append(
        ExposureHistoryEntry(id=str(uuid.uuid4()), career_id=career_id, shown_at=now, interaction=interaction)  # type: ignore[arg-type]
    )
