from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ExposureHistoryEntry(BaseModel):
    """One real Exposure Universe suggestion event — distinct from
    ``career_exploration_history``'s real-visit log: this tracks whether
    a career was *surfaced as an exposure suggestion*, so repeats are
    genuinely avoided. A brand-new, separate top-level `StudentProfile`
    field (Discover Batch 1 is frozen — this is never nested inside
    `discovery_onboarding`)."""

    id: str
    career_id: str
    shown_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    interaction: Literal["shown", "opened", "dismissed"] = "shown"
