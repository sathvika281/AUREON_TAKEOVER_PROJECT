from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

#: Never LLM-asserted — always computed from real deltas in
#: agents/specialized/growth/evidence_summary.py, mirroring the
#: deterministic-ceiling philosophy used for confidence everywhere else
#: in this codebase (hypothesis lifecycle, candidate confidence, etc.).
ProgressDirection = Literal["improving", "steady", "slowing", "not_enough_evidence"]


class ProgressDimension(BaseModel):
    """One dimension of the student's growth, backed by real evidence
    only — there is no dimension in this model without a genuine data
    source behind it (see evidence_summary.py's docstring for exactly
    which StudentProfile fields back each one)."""

    key: str
    label: str
    direction: ProgressDirection
    #: Deterministic, real facts (counts/deltas) — never LLM-invented.
    evidence_summary: list[str] = Field(default_factory=list)
    #: The LLM's explanation of *why*, grounded in evidence_summary above.
    reasoning: str = ""


class ProgressTimelineWindow(BaseModel):
    """A pure read-aggregation window (Last Week / Last Month / Overall
    Journey) — deterministic, no LLM involved, same philosophy as
    decision_timeline.py."""

    label: str
    description: str
    event_count: int


class ProgressPriority(BaseModel):
    """One ranked next action — always cites the specific evidence behind
    it. This single list serves both "recommendations" and "next
    priority" from the spec, since every entry already answers both
    questions."""

    rank: int
    action: str
    evidence: str


class ProgressReport(BaseModel):
    """Progress Intelligence's one structured artifact. Never persisted —
    computed fresh from data StudentProfile already stores, exactly like
    decision_timeline.py's pure-read pattern plus one LLM call for the
    narrative layer."""

    overall_narrative: str
    dimensions: list[ProgressDimension] = Field(default_factory=list)
    growing_strengths: list[str] = Field(default_factory=list)
    areas_slowing_down: list[str] = Field(default_factory=list)
    recent_improvements: list[str] = Field(default_factory=list)
    timeline: list[ProgressTimelineWindow] = Field(default_factory=list)
    next_priorities: list[ProgressPriority] = Field(default_factory=list)
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
