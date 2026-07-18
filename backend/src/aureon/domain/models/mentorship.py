from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

MentorshipStatus = Literal["requested", "accepted", "declined", "completed"]
MentorshipNoteAuthorRole = Literal["student", "expert"]


class MentorshipProgressNote(BaseModel):
    """One note on an ongoing mentorship — embedded directly on the
    ``Mentorship`` row (unlike ``SharedSessionNote``, which the prior
    batch split into its own table) since a mentorship's notes are
    always fetched/updated together with their one parent relationship,
    with no independent cross-mentorship querying need."""

    id: str
    author_role: MentorshipNoteAuthorRole
    note: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Mentorship(BaseModel):
    """The real relationship ``Mentor.accepts_mentorship``/
    ``max_students`` were built for in Connect Batch 1 — never a second
    Expert/profile model. Standalone table (not embedded on
    ``StudentProfile``) since an expert must be able to query requests
    across every student, which is structurally impossible against a
    per-student jsonb blob — same reasoning ``SharedSession`` used.

    There is no expert-side login anywhere in this system, so an
    expert's review/accept/decline happens via the opaque
    ``review_token`` below — the exact same "second party this system
    can't authenticate" pattern ``SharedSession`` already solved.
    """

    id: str
    student_id: str
    expert_id: str
    review_token: str
    status: MentorshipStatus = "requested"
    goals: str = ""
    progress_notes: list[MentorshipProgressNote] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
