from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

MissionTier = Literal["still_emerging", "growing", "strong"]
MissionTrend = Literal["emerging", "steady", "fading", "not_enough_evidence"]
MissionEvidenceSource = Literal["career_dna", "experiment", "reflection", "evidence_graph"]


class LifeMission(BaseModel):
    """One entry in the Life Missions catalog — a kind of real-world
    impact a student might resonate with (e.g. "Solve Climate
    Problems"), not a career recommendation. Data, not prompt text — same
    illustrative-composite honesty convention as every other seeded
    knowledge base. Purely data-driven: domain/services/life_mission_engine.py
    reads only `related_tags`/`name`, never a mission's identity, so a new
    mission is a seed-row insert, never a code change."""

    id: str
    name: str
    description: str
    famous_people: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    nonprofits: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    documentaries: list[str] = Field(default_factory=list)
    podcasts: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    real_world_examples: list[str] = Field(default_factory=list)
    suggested_careers: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    volunteering_opportunities: list[str] = Field(default_factory=list)
    research_areas: list[str] = Field(default_factory=list)
    startup_ideas: list[str] = Field(default_factory=list)
    #: Cross-reference tags used by life_mission_engine.py's matching
    #: heuristic — case-insensitive substring overlap against real
    #: student evidence.
    related_tags: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite overview compiled for exploration — real, "
        "well-known people and organizations, not a continuously verified "
        "or exhaustive directory."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MissionEvidenceItem(BaseModel):
    """A single real, concrete fact backing a MissionResonance — never a
    generic platitude. Same shape as domain/models/talent.py's
    TalentEvidenceItem, applied to a different evidence domain."""

    source: MissionEvidenceSource
    description: str
    observed_at: datetime


class MissionResonance(BaseModel):
    """Output of domain/services/life_mission_engine.py::analyze_life_missions.
    ``tier`` is never a numeric score and never claims certainty; ``trend``
    is a real, timestamp-derived direction, never fabricated."""

    mission: LifeMission
    tier: MissionTier
    trend: MissionTrend
    explanation: str
    evidence: list[MissionEvidenceItem]
