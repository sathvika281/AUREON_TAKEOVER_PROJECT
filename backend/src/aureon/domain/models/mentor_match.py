from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

#: Same active/discarded posture as CareerCandidate — an evolving belief,
#: not a one-off computation. Not literally the same class (Phase 2 stays
#: untouched), but the identical lifecycle pattern.
MatchStatus = Literal["active", "discarded"]


class MentorMatch(BaseModel):
    id: str
    mentor_id: str
    mentor_name: str
    why_it_matches: str
    confidence: float  # internal only — never shown to the student as a raw number
    uncertainty_reason: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    status: MatchStatus = "active"
    transition_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollegeMatch(BaseModel):
    id: str
    institution_id: str
    institution_name: str
    why_it_matches: str
    confidence: float
    uncertainty_reason: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    status: MatchStatus = "active"
    transition_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
