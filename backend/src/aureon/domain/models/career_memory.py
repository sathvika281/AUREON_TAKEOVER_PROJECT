"""Responsibility: Career Memory's data shapes — Aureon's shared,
persistent understanding of a student, organized around Identity /
Evidence / Opportunities / Connections / Growth. Owns: only the fields
with no existing home elsewhere on ``StudentProfile``. Does NOT own:
anything ``StudentProfile`` already tracks (``interests``, ``strengths``,
``values``, ``goals``, ``career_dna``, ``mentor_matches``,
``mentor_interactions``, ``learning_progress`` all stay exactly where
they are) — those are read live, never duplicated here. Consumed by:
``services/foundation/career_memory/service.py`` only; every other
component reads Career Memory through that service, never these models
directly.

Reference vs. new data, by field:
- ``EvidenceArtifact.ref_id`` and ``OpportunityEntry.ref_id`` are
  references to an existing record elsewhere (never a copy) —
  ``OpportunityEntry.ref_id`` points at a real
  ``domain.models.opportunity.Opportunity.id``.
- ``Connection``/``ConnectionsMemory`` are fully derived on read from
  ``StudentProfile.mentor_matches``/``mentor_interactions`` — zero
  storage of their own.
- ``IdentityMemory.preferred_industries``/``academic_level``/
  ``location_country``, ``GrowthSkill``, ``GrowthMission``,
  ``InterviewPracticeRecord``, and ``OpportunitiesMemory.score_history``
  are genuinely new data with no existing entity anywhere in
  ``StudentProfile`` to reference.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from aureon.domain.models.opportunity import OpportunityCategory


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IdentityMemory(BaseModel):
    """Everything else identity-related (interests, strengths, values,
    goals, Career DNA) is read live from StudentProfile — this is only
    the one field with no existing home. `academic_level`/
    `location_country` were added for Opportunity Hub's Academic
    Eligibility/Location scoring factors — genuinely new signals Stage
    1 never captured; `None` scores neutral, never fabricated/penalized."""

    preferred_industries: list[str] = Field(default_factory=list)
    academic_level: Literal["high_school", "undergraduate", "graduate"] | None = None
    location_country: str | None = None


class EvidenceArtifact(BaseModel):
    """A reference to something that proves ability — never a copy of
    the underlying record (GitHub investigation, document investigation,
    etc.)."""

    kind: Literal["project", "github_repo", "resume", "certificate", "research_paper", "portfolio", "achievement"]
    ref_id: str
    title: str
    added_at: datetime = Field(default_factory=_utcnow)


class EvidenceMemory(BaseModel):
    artifacts: list[EvidenceArtifact] = Field(default_factory=list)


class OpportunityEntry(BaseModel):
    """`interaction` is the real student action; `category` is the
    opportunity's own type — previously conflated into one `kind` field
    (a documented Stage 1 gap, fixed here now that Opportunity Hub's
    Knowledge Base exists). `ref_id` now always points at a real
    `Opportunity.id`, never a copy of the opportunity's own fields, same
    reference-only convention as `EvidenceArtifact.ref_id`.
    `opportunity_version` captures the real `Opportunity.version` at
    interaction time, so this historical record stays a truthful
    statement about what the student saw then, even after the
    opportunity's real details later change."""

    interaction: Literal["viewed", "saved", "applied", "withdrawn", "completed"]
    category: OpportunityCategory
    ref_id: str | None = None
    opportunity_version: int | None = None
    title: str
    occurred_at: datetime = Field(default_factory=_utcnow)


class OpportunitiesMemory(BaseModel):
    entries: list[OpportunityEntry] = Field(default_factory=list)
    #: opportunity_id -> last computed overall_score — the real state
    #: behind Opportunity Hub's score-smoothing/stability mechanism (see
    #: agents/specialized/opportunity/scoring.py).
    score_history: dict[str, float] = Field(default_factory=dict)


class Connection(BaseModel):
    """Fully derived, never separately stored — see
    ``career_memory/service.py::get_connections``."""

    mentor_id: str
    mentor_name: str
    connected_at: datetime
    conversation_summary: str | None = None


class ConnectionsMemory(BaseModel):
    connections: list[Connection] = Field(default_factory=list)


class GrowthSkill(BaseModel):
    skill: str
    status: Literal["in_progress", "mastered"]
    evidence: str


class GrowthMission(BaseModel):
    mission_id: str
    status: Literal["current", "completed"]


class InterviewPracticeRecord(BaseModel):
    conducted_at: datetime
    weak_areas: list[str] = Field(default_factory=list)
    feedback_summary: str


class GrowthMemory(BaseModel):
    """Skills, missions, and interview practice — consolidated under one
    domain matching GrowthAgent's existing real ownership of missions/
    skill evolution/career readiness. Deliberately distinct from
    ``StudentProfile.learning_progress`` (roadmap-specific), which stays
    untouched, not duplicated here."""

    skills: list[GrowthSkill] = Field(default_factory=list)
    missions: list[GrowthMission] = Field(default_factory=list)
    interview_practice: list[InterviewPracticeRecord] = Field(default_factory=list)


class CareerMemory(BaseModel):
    """The one combined read/write surface every future Phase 2 agent
    uses — see ``get_career_memory_snapshot``. Nests all five domains;
    stays honestly empty wherever no real feature has populated it yet
    (no fabricated sample data)."""

    identity: IdentityMemory = Field(default_factory=IdentityMemory)
    evidence: EvidenceMemory = Field(default_factory=EvidenceMemory)
    opportunities: OpportunitiesMemory = Field(default_factory=OpportunitiesMemory)
    connections: ConnectionsMemory = Field(default_factory=ConnectionsMemory)
    growth: GrowthMemory = Field(default_factory=GrowthMemory)
    updated_at: datetime = Field(default_factory=_utcnow)
