from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CareerWorld(BaseModel):
    """One entry in the Missing Worlds catalog — an entire career
    ecosystem (e.g. "Space," "Biotechnology"), not a single career. Data,
    not prompt text — same illustrative-composite honesty convention as
    every other seeded knowledge base in this codebase (Trends, Careers,
    Experiments). Purely data-driven: domain/services/missing_worlds_engine.py
    reads only `related_industries`/`name`, never a world's identity, so a
    new world is a seed-row insert, never a code change."""

    id: str
    name: str
    description: str
    why_it_matters: str
    global_importance: str
    future_growth: str
    famous_careers: list[str] = Field(default_factory=list)
    beginner_roadmap: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    #: Cross-reference tags used by missing_worlds_engine.py's matching
    #: heuristic — case-insensitive substring overlap against real
    #: student signal fragments.
    related_industries: list[str] = Field(default_factory=list)
    videos: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    beginner_projects: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    colleges: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite overview compiled for exploration — real, "
        "well-known organizations and resources, not a continuously "
        "verified or exhaustive directory."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
