from datetime import datetime, timezone

from pydantic import BaseModel, Field


class TopicResourceDomain(BaseModel):
    """One entry in the shared topic-keyed exploration resource catalog
    (e.g. "Space & Astronomy") — deliberately distinct from Missing
    Worlds' CareerWorld: exploration/curiosity-shaped content (creators,
    hackathons, museums, challenge platforms), never career-outcome-
    shaped content (no colleges/companies/internships here). Composed
    into Knowledge Circles' resource lists (domain/services/
    knowledge_circle_service.py). Purely data-driven — a new domain is a
    seed-row insert, never a code change."""

    id: str
    name: str
    keywords: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    documentaries: list[str] = Field(default_factory=list)
    podcasts: list[str] = Field(default_factory=list)
    youtube_channels: list[str] = Field(default_factory=list)
    creators: list[str] = Field(default_factory=list)
    communities: list[str] = Field(default_factory=list)
    competitions: list[str] = Field(default_factory=list)
    workshops: list[str] = Field(default_factory=list)
    hackathons: list[str] = Field(default_factory=list)
    research_organizations: list[str] = Field(default_factory=list)
    museums_and_science_centers: list[str] = Field(default_factory=list)
    exhibitions_and_conferences: list[str] = Field(default_factory=list)
    journals_and_newsletters: list[str] = Field(default_factory=list)
    learning_platforms: list[str] = Field(default_factory=list)
    open_source_projects: list[str] = Field(default_factory=list)
    challenge_platforms: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite overview compiled for exploration — real, "
        "well-known creators and organizations, not a continuously "
        "verified or exhaustive directory."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
