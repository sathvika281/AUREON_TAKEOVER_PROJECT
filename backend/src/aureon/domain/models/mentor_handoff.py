from datetime import datetime, timezone

from pydantic import BaseModel, Field


class MentorHandoff(BaseModel):
    """Represents a single human-in-the-loop handoff.

    The orchestrator can request a handoff at any point regardless of
    confidence stage (unlike Career Intelligence/Decision/Roadmap, the
    Mentor Agent is not gated by ``MIN_RECOMMENDATION_CONFIDENCE`` — a
    confused student early in Exploration Mode may need a mentor most).
    Resolved handoffs are appended to the student's long-term profile so
    mentor interactions become part of their ongoing journey, not a
    one-off event.
    """

    reason: str
    requested_by_agent: str
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: datetime | None = None
    mentor_id: str | None = None
