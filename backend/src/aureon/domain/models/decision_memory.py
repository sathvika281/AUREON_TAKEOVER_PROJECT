from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

#: "simulated" added in V11 (Career Simulator) — additive alongside the
#: existing action types.
DecisionMemoryActionType = Literal["compared", "shortlisted", "removed", "simulated"]


class DecisionMemoryEntry(BaseModel):
    """A short, explained log of decision-relevant actions — distinct
    from Career Exploration History (purely observational, no reasoning
    attached) and from the full CareerComparison record (the detailed
    matrix). This is the human-readable "why" trail: what was compared,
    shortlisted, or removed, and why, in one sentence.

    Every reason is derived from data already computed elsewhere (a
    comparison's own summary, or a candidate's evidence_strength/
    missing_evidence) — never a fresh, separate LLM call.
    """

    id: str
    action_type: DecisionMemoryActionType
    career_ids: list[str]
    career_names: dict[str, str] = Field(default_factory=dict)
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
