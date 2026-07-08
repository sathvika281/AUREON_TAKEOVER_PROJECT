from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

#: Investigating -> Growing -> Strong -> Validated is the "confidence
#: grows" path; Discarded can happen from any state when the LLM stops
#: returning this hypothesis. Status is always computed deterministically
#: from the real confidence number (see hypothesis_lifecycle.py) — never
#: asserted by the LLM itself, since hallucinated status would be exactly
#: the kind of unearned confidence this product refuses to allow.
HypothesisStatus = Literal["investigating", "growing", "strong", "validated", "discarded"]


class CareerHypothesis(BaseModel):
    """A tentative, evolving guess about a career direction — deliberately
    the opposite of a confident recommendation. The Hypothesis Engine
    (Discovery Agent) thinks like a scientist: it states what's still
    missing, tracks a confidence level, and revises as more evidence
    arrives rather than committing early.

    Supporting and contradicting evidence are *not* stored here — they're
    computed by filtering ``StudentProfile.evidence_graph`` for this
    hypothesis's ``career_name`` when an API response is built, so there
    is exactly one place evidence lives. ``missing_evidence`` stays a
    plain string list since a gap isn't evidence.
    """

    career_name: str
    confidence: float
    missing_evidence: list[str] = Field(default_factory=list)
    status: HypothesisStatus = "investigating"
    transition_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
