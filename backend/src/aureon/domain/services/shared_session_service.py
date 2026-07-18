"""Responsibility: Shared (Joint) Session business logic — creating an
invite, a second participant joining via token, adding shared notes,
and status transitions. Owns: `create_invite`, `join_as_participant`,
`add_note`, `schedule`, `complete`. Does NOT own persistence
(`shared_session_repository.py`) or slot generation (reuses
`career_experience_view.py::generate_available_slots` verbatim — never
reinvented). Consumed by: `api/v1/parent_connect.py`.
"""

import uuid
from datetime import datetime, timezone

from aureon.domain.models.mentor import Mentor
from aureon.domain.models.shared_session import SharedSession, SharedSessionNote


def create_invite(*, student_id: str, mentor: Mentor, career_id: str | None, topic: str) -> SharedSession:
    """`mentor_id`/expert identity is always read from the real `Mentor`
    record, never trusted from client input — same discipline as
    `career_experience_actions.py::add_expert_session_booking`."""
    return SharedSession(
        id=str(uuid.uuid4()),
        student_id=student_id,
        mentor_id=mentor.id,
        career_id=career_id,
        access_token=str(uuid.uuid4()),
        topic=topic,
    )


def join_as_participant(session: SharedSession, *, participant_label: str) -> SharedSession:
    updated = session.model_copy(
        update={
            "participant_label": participant_label,
            "status": "scheduled" if session.scheduled_slot else session.status,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    return updated


def schedule(session: SharedSession, *, slot: datetime) -> SharedSession:
    return session.model_copy(
        update={"scheduled_slot": slot, "status": "scheduled", "updated_at": datetime.now(timezone.utc)}
    )


def complete(session: SharedSession) -> SharedSession:
    return session.model_copy(update={"status": "completed", "updated_at": datetime.now(timezone.utc)})


def build_note(session_id: str, *, author_role: str, note: str) -> SharedSessionNote:
    return SharedSessionNote(id=str(uuid.uuid4()), session_id=session_id, author_role=author_role, note=note)
