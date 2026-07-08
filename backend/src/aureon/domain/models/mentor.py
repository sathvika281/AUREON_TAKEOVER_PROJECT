from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Mentor(BaseModel):
    """One entry in the Mentor Knowledge Base — data, not prompt text, same
    treatment as the Career Knowledge Base. ``name`` is an illustrative
    persona label (e.g. "Dr. Priya Nair, Materials Science Professor"),
    not a claim of a specific real, contactable individual — same honesty
    convention as Phase 2's Human Stories.
    """

    id: str
    name: str
    role_type: str  # professor | researcher | industry_professional | founder | creator
    field: str
    bio: str
    trait_tags: list[str] = Field(default_factory=list)  # same TRAIT_NAMES vocabulary as careers
    learning_style_fit: str
    #: V13 — Expert Connect; additive, richer profile fields for the
    #: existing Mentor Knowledge Base entries (no new parallel "Expert"
    #: model — an expert *is* a Mentor).
    organization: str = ""
    years_experience: int = 0
    journey_highlights: list[str] = Field(default_factory=list)
    discussion_topics: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
