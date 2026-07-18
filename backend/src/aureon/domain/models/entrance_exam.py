from datetime import datetime, timezone

from pydantic import BaseModel, Field


class EntranceExam(BaseModel):
    """One real entrance exam, independent of any single institution —
    a national exam is accepted by many institutions, so this is a
    genuinely separate entity (not a `research_labs`-style 1-institution-
    owns-N-children row). `accepted_institution_ids` is a denormalized
    membership list rather than a join table — deliberately simple for a
    small (~5-10 row), rarely-updated catalog, matching Institution's own
    documented "don't over-normalize" philosophy."""

    id: str
    name: str
    description: str
    eligibility: list[str] = Field(default_factory=list)
    preparation_guidance: str
    typical_timeline: str
    accepted_institution_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
