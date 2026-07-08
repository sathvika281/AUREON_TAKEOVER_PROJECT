from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Turn(BaseModel):
    """A single message within a conversation."""

    role: Literal["student", "assistant"]
    content: str
    agent_name: str | None = None  # which agent produced this turn, if role == "assistant"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    """A single session-scoped conversation. Unlike ``StudentProfile``, this
    resets/starts fresh per session — it is the raw transcript, not the
    accumulated long-term understanding of the student."""

    conversation_id: str
    student_id: str
    turns: list[Turn] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
