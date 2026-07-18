"""Responsibility: Institution Profile — a compact, 4-dimension visual
summary (Research / Entrepreneurship / Campus Life / International
Exposure) shown before a student dives into an institution's full
detail page. Pure, deterministic, computed fresh on every read from
real counts already on the institution's own fetched data — same
philosophy as Hidden Potential/Talent Pattern Engine. Explicitly *not*
a ranking: each dimension is a real count-to-tier mapping, never a
fabricated or LLM-generated number, never persisted.
"""

from dataclasses import dataclass

from aureon.domain.models.institution import (
    InnovationCenter,
    Institution,
    ResearchLab,
    StudentOrganization,
)

MAX_STARS = 5


@dataclass(frozen=True)
class InstitutionProfile:
    research: int
    entrepreneurship: int
    campus_life: int
    international_exposure: int


def _tier_from_count(count: int, thresholds: tuple[int, int, int, int]) -> int:
    """1-5 stars from a real count against 4 ascending thresholds —
    same deterministic-ceiling philosophy used everywhere else in this
    codebase (e.g. Talent Pattern Engine's evidence-count tiers)."""
    for tier, threshold in enumerate(thresholds, start=2):
        if count < threshold:
            return tier - 1
    return MAX_STARS


def compute_institution_profile(
    institution: Institution,
    *,
    research_labs: list[ResearchLab],
    innovation_centers: list[InnovationCenter],
    student_organizations: list[StudentOrganization],
) -> InstitutionProfile:
    campus_life_count = (
        len(student_organizations) + len(institution.hostels) + len(institution.campus_facilities)
    )
    return InstitutionProfile(
        research=_tier_from_count(len(research_labs), (1, 2, 4, 6)),
        entrepreneurship=_tier_from_count(len(innovation_centers), (1, 2, 3, 4)),
        campus_life=_tier_from_count(campus_life_count, (2, 4, 7, 10)),
        international_exposure=_tier_from_count(len(institution.exchange_programs), (1, 2, 3, 4)),
    )
