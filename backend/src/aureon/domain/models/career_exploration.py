from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

#: Observational only — recording that a student looked at, bookmarked, or
#: returned to a career says nothing on its own about fit or preference.
#: Never fed into the Evidence Graph or Career Candidate reasoning; Phase
#: 3's Decision Agent is expected to interpret patterns across these
#: events, not this module.
CareerInteractionType = Literal[
    "opened",
    "revisited",
    "bookmarked",
    "removed",
    "story_viewed",
    "future_lens_explored",
    "reality_read",
    "compared",
    #: V11 — Career Simulator, additive alongside "compared".
    "simulated",
]


class CareerExplorationEvent(BaseModel):
    """One observed interaction with a career in the Knowledge Base —
    exploration behavior, not a decision or a piece of evidence."""

    id: str
    career_id: str
    interaction_type: CareerInteractionType
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
