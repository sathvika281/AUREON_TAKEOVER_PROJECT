from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ExpertSessionBooking(BaseModel):
    """A real, student-initiated request to meet an expert at a specific
    time — persisted honestly as a request, never simulated as
    auto-accepted (no real video-calling/calendar integration exists;
    see V13 spec's explicit constraint)."""

    id: str
    mentor_id: str
    mentor_name: str
    slot_start: datetime
    topic: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GuidanceRequest(BaseModel):
    """A lighter alternative to booking a specific slot — for experts
    without exposed availability, or students who'd rather just ask."""

    id: str
    mentor_id: str
    mentor_name: str
    message: str
    status: Literal["requested"] = "requested"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventRegistration(BaseModel):
    id: str
    event_id: str
    event_title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
