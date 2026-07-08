from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ReflectionEntry(BaseModel):
    """One prompt/response pair in the student's Reflection Journal. Every
    meaningful interaction (a conversation topic, an exploration activity)
    should end with a reflection; the response becomes evidence for
    Career DNA rather than being discarded after the chat scrolls past."""

    prompt: str
    response: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    answered_at: datetime | None = None
