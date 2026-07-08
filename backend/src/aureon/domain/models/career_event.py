from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

EventType = Literal["workshop", "hackathon", "open_day", "career_talk"]


class CareerEvent(BaseModel):
    """One entry in the shared Experience Events Knowledge Base (V13) —
    workshops/hackathons/open days are institution-hosted
    (``institution_id`` set), career talks are mentor-hosted
    (``mentor_id`` set); same shape either way, exactly one host field
    populated. Internal name stays ``CareerEvent``; students see these
    as "Experience Events," never "Career Events" (broader than careers
    alone — research sessions, hackathons, etc.)."""

    id: str
    title: str
    event_type: EventType
    institution_id: str | None = None
    mentor_id: str | None = None
    description: str
    scheduled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
