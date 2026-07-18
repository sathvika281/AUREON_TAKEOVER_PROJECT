"""Responsibility: deterministic, zero-AI opportunity filtering across
14 dimensions. Owns: `OpportunityFilters`, `apply_filters`. Does NOT
own: relevance/semantic matching (search.py) or fit scoring (scoring.py)
— filtering only ever removes opportunities that fail a hard, factual
constraint. Consumed by: `OpportunityAgent.find_opportunities`.

No AI logic inside filters — every check here is a plain equality,
membership, or range comparison against real `Opportunity` fields.
"""

from dataclasses import dataclass
from datetime import datetime

from aureon.domain.models.opportunity import (
    AcademicLevel,
    CompetitivenessLevel,
    DifficultyLevel,
    Opportunity,
    OpportunityCategory,
    OrganizationKind,
)

#: Same ladder order scoring.py's Academic Eligibility factor uses —
#: kept as its own small local constant rather than importing a private
#: name from scoring.py, since this is a 3-item list unlikely to drift.
_ACADEMIC_LADDER = ["high_school", "undergraduate", "graduate"]


@dataclass(frozen=True)
class OpportunityFilters:
    """All 14 filter dimensions. Every field is `None`/empty by default,
    meaning "no constraint" — a filter only narrows results when a
    caller actually sets it."""

    categories: frozenset[OpportunityCategory] | None = None
    is_remote: bool | None = None
    countries: frozenset[str] | None = None
    paid: bool | None = None
    max_academic_level: AcademicLevel | None = None
    difficulty_levels: frozenset[DifficultyLevel] | None = None
    max_competitiveness: CompetitivenessLevel | None = None
    organization_kinds: frozenset[OrganizationKind] | None = None
    required_skills_any: frozenset[str] | None = None
    domain_tags_any: frozenset[str] | None = None
    min_duration_weeks: float | None = None
    max_duration_weeks: float | None = None
    deadline_before: datetime | None = None
    deadline_after: datetime | None = None


_COMPETITIVENESS_ORDER = ["low", "medium", "high", "very_high"]


def _passes(opportunity: Opportunity, filters: OpportunityFilters) -> bool:
    if filters.categories is not None and opportunity.category not in filters.categories:
        return False
    if filters.is_remote is not None and opportunity.is_remote != filters.is_remote:
        return False
    if filters.countries is not None:
        if not opportunity.is_remote and opportunity.countries and not (
            set(opportunity.countries) & filters.countries
        ):
            return False
    if filters.paid is not None and opportunity.paid != filters.paid:
        return False
    if filters.max_academic_level is not None and opportunity.min_academic_level != "any":
        if _ACADEMIC_LADDER.index(opportunity.min_academic_level) > _ACADEMIC_LADDER.index(
            filters.max_academic_level
        ):
            return False
    if filters.difficulty_levels is not None and opportunity.difficulty_level not in filters.difficulty_levels:
        return False
    if filters.max_competitiveness is not None:
        if _COMPETITIVENESS_ORDER.index(opportunity.estimated_competitiveness) > _COMPETITIVENESS_ORDER.index(
            filters.max_competitiveness
        ):
            return False
    if filters.organization_kinds is not None and opportunity.organization_kind not in filters.organization_kinds:
        return False
    if filters.required_skills_any is not None:
        required_lower = {s.lower() for s in opportunity.required_skills}
        if not (required_lower & {s.lower() for s in filters.required_skills_any}):
            return False
    if filters.domain_tags_any is not None:
        tags_lower = {t.lower() for t in opportunity.domain_tags}
        if not (tags_lower & {t.lower() for t in filters.domain_tags_any}):
            return False
    if filters.min_duration_weeks is not None:
        if opportunity.duration_weeks is None or opportunity.duration_weeks < filters.min_duration_weeks:
            return False
    if filters.max_duration_weeks is not None:
        if opportunity.duration_weeks is None or opportunity.duration_weeks > filters.max_duration_weeks:
            return False
    if filters.deadline_before is not None:
        if opportunity.application_deadline is None or opportunity.application_deadline > filters.deadline_before:
            return False
    if filters.deadline_after is not None:
        if opportunity.application_deadline is None or opportunity.application_deadline < filters.deadline_after:
            return False
    return True


def apply_filters(opportunities: list[Opportunity], filters: OpportunityFilters) -> list[Opportunity]:
    return [o for o in opportunities if _passes(o, filters)]
