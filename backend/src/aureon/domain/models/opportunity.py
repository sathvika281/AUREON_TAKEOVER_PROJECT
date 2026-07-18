"""Responsibility: the Opportunity Knowledge Base's own data shape.
Owns: `Opportunity` and its supporting literals/sub-models. Does NOT
own: how opportunities are fetched (a Provider's job, see
agents/specialized/opportunity/providers/) or how a student's fit
against one is scored (scoring.py). Consumed by: the Opportunity
Repository, Providers, and OpportunityAgent's scoring/filtering/search
modules.

Real, structured content, not prompt text — the same honesty
convention as domain/models/institution.py's StudentAmbassador/
StudentProject: illustrative composite postings proving the matching
architecture, never claimed as live/currently-open/contactable listings
scraped from real organizations (see `source_note`).
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

OpportunityCategory = Literal[
    "internship",
    "hackathon",
    "research_program",
    "competition",
    "scholarship",
    "open_source_program",
    "fellowship",
    "campus_ambassador_program",
    "conference",
    "workshop",
    "bootcamp",
    "innovation_challenge",
    # Explore Polish Batch — additive, matches Opportunity Equality's
    # explicit ask (government schemes, mentorship, free certifications,
    # funding, communities) that had no first-class category before.
    "government_scheme",
    "mentorship_program",
    "certification",
    "funding_grant",
    "community_program",
]
DifficultyLevel = Literal["beginner", "intermediate", "advanced"]
CompetitivenessLevel = Literal["low", "medium", "high", "very_high"]
AcademicLevel = Literal["high_school", "undergraduate", "graduate", "any"]
OrganizationKind = Literal["university", "company", "nonprofit", "government", "community"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OpportunityTimelineStep(BaseModel):
    label: str
    detail: str
    date: datetime | None = None


class Opportunity(BaseModel):
    """One posting in the Opportunity Knowledge Base. Plain string lists
    for eligibility/benefits/application_steps/required_documents —
    this KB is small (~18 rows) and single-provider-agnostic, so
    normalizing further into child tables buys nothing (same reasoning
    domain/models/institution.py already documents for its own
    similarly-sized sub-entities).

    `version` increments only when real content changes (deadline
    moved, eligibility edited, benefits updated) — see
    OpportunityRepository.upsert_opportunity. The recommendation engine
    always reads the current row; Career Memory's OpportunityEntry
    separately captures the version at interaction time, so a
    historical "saved" record stays a truthful statement about what the
    student saw then, even after this row later changes.
    """

    id: str
    version: int = 1
    title: str
    category: OpportunityCategory
    organization: str
    organization_kind: OrganizationKind
    description: str
    eligibility: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_academic_level: AcademicLevel = "any"
    #: e.g. ["ai", "robotics"] — used by Career Alignment scoring and
    #: keyword-based semantic search.
    domain_tags: list[str] = Field(default_factory=list)
    location: str
    is_remote: bool = False
    #: Empty = open to all countries.
    countries: list[str] = Field(default_factory=list)
    paid: bool = False
    compensation_summary: str | None = None
    duration_label: str
    duration_weeks: float | None = None
    difficulty_level: DifficultyLevel = "intermediate"
    estimated_competitiveness: CompetitivenessLevel = "medium"
    #: None = rolling/no fixed deadline.
    application_deadline: datetime | None = None
    application_steps: list[str] = Field(default_factory=list)
    timeline: list[OpportunityTimelineStep] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    official_link: str
    required_documents: list[str] = Field(default_factory=list)
    #: Same honesty convention as institution.py's StudentAmbassador/StudentProject.
    source_note: str = (
        "Illustrative composite posting for Opportunity Hub's knowledge base — "
        "not a claim of a live, currently-open external listing."
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
