"""Responsibility: Shared Session — the scheduling/architecture
primitive for a student + a second participant (parent, guardian,
sibling, teacher, counselor — deliberately generic) to jointly meet an
expert. "Shared Session" is the internal name; every user-visible
string calls this a "Joint Session." Actual live calling/video is out
of scope — this is the architecture and shared-notes data model only.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

SharedSessionStatus = Literal["invited", "scheduled", "completed", "cancelled"]
SharedSessionAuthorRole = Literal["student", "participant", "expert"]


class SharedSession(BaseModel):
    """A parent/guardian has no student auth, so this session must be
    independently fetchable via `access_token` alone — never embedded
    on `StudentProfile` like `ExpertSessionBooking`."""

    id: str
    student_id: str
    mentor_id: str
    career_id: str | None = None
    access_token: str
    #: Free-text description of who's joining — "Mom", "Ms. Rodriguez
    #: (counselor)", "older brother" — deliberately generic, never
    #: assumed to literally be a parent.
    participant_label: str = ""
    topic: str
    status: SharedSessionStatus = "invited"
    scheduled_slot: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SharedSessionNote(BaseModel):
    id: str
    session_id: str
    author_role: SharedSessionAuthorRole
    note: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
