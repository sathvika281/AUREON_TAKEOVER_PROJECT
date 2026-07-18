from datetime import datetime, timezone

from pydantic import BaseModel, Field


class KnowledgeCircle(BaseModel):
    """One curated, per-domain learning hub — NOT a social feed (no
    likes/followers/posts/comments). Reuses ``CareerWorld``'s 31
    already-curated domain names as its seed domain set (one
    ``KnowledgeCircle`` per ``CareerWorld``) rather than inventing a
    fifth, competing taxonomy.

    Only carries the fields genuinely missing from every existing
    catalog model — every other requested resource category (books,
    documentaries, podcasts, YouTube channels, journals/newsletters,
    conferences, competitions, hackathons, workshops, communities,
    open-source projects, research organizations, museums, companies,
    universities, certifications, research papers, government
    initiatives, volunteering opportunities) is composed at read time
    from the linked ``CareerWorld``, ``TopicResourceDomain``(s),
    matching ``Career`` rows, matching ``Trend`` rows, and matching
    ``LifeMission`` rows — never re-typed here. See
    ``knowledge_circle_service.py::build_circle_view``.
    """

    id: str
    name: str
    overview: str
    what_this_field_is_about: str
    beginner_projects: list[str] = Field(default_factory=list)
    advanced_projects: list[str] = Field(default_factory=list)
    laboratories: list[str] = Field(default_factory=list)
    startups: list[str] = Field(default_factory=list)
    ngos: list[str] = Field(default_factory=list)
    scholarships: list[str] = Field(default_factory=list)
    #: Reuse links — never resolved/denormalized onto this row.
    linked_career_world_id: str | None = None
    linked_topic_domain_ids: list[str] = Field(default_factory=list)
    #: Matched case-insensitively against ``Career.industry``.
    related_career_industries: list[str] = Field(default_factory=list)
    related_trend_ids: list[str] = Field(default_factory=list)
    related_life_mission_ids: list[str] = Field(default_factory=list)
    source_note: str = (
        "Illustrative composite learning hub compiled for exploration — "
        "composed from Aureon's own curated catalogs, not a continuously "
        "verified or exhaustive directory."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
