from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

#: Mirrors CareerHypothesis's discard behavior: a candidate absent from a
#: later analysis is kept (not deleted, so its history survives) but
#: marked discarded rather than lingering indefinitely as if still live.
#: No investigating/growing/strong bucketing here — that distinction is
#: already carried by confidence/evidence_strength; candidates only need
#: to distinguish "still a live possibility" from "no longer surfaced."
CareerCandidateStatus = Literal["active", "discarded"]


class CareerCandidate(BaseModel):
    """A career the Career Intelligence Agent has reasoned about as a
    possible fit — deliberately not a "recommendation": every candidate
    carries its own uncertainty and can be revised as more evidence
    arrives, same evolving-belief posture as ``CareerHypothesis``.

    Supporting/contradicting evidence is *not* stored here — computed by
    filtering ``StudentProfile.evidence_graph`` for this candidate's
    ``career_id`` (``related_career``), same single-source-of-truth
    pattern as hypotheses. ``confidence`` is internal only: it drives
    sorting and the deterministic Evidence Strength label
    (``career_intelligence/confidence.py``) but is never shown to the
    student as a raw number.
    """

    id: str
    career_id: str
    career_name: str
    why_it_matches: str
    confidence: float
    uncertainty_reason: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    status: CareerCandidateStatus = "active"
    transition_reason: str | None = None
    #: Phase 3 — an explicit student action (not agent-derived), reusing
    #: this existing model rather than a parallel one. Independent of
    #: `status`: a shortlisted candidate can still later be discarded.
    is_shortlisted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
