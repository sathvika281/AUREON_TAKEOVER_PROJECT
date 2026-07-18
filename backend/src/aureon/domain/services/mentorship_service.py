"""Responsibility: Mentorship business logic — requesting, an expert's
accept/decline/complete, and progress notes. Owns: ``request_mentorship``,
``accept``, ``decline``, ``complete``, ``add_note``,
``count_active_mentees``. Does NOT own persistence
(``mentorship_repository.py``). Consumed by: ``api/v1/mentorship.py``.
"""

import uuid
from datetime import datetime, timezone

from aureon.domain.models.mentor import Mentor
from aureon.domain.models.mentorship import Mentorship, MentorshipNoteAuthorRole, MentorshipProgressNote


def request_mentorship(*, student_id: str, expert: Mentor, goals: str) -> Mentorship:
    """``expert_id`` is always read from the real ``Mentor`` record,
    never trusted from client input — same discipline as
    ``shared_session_service.py::create_invite``."""
    return Mentorship(
        id=str(uuid.uuid4()),
        student_id=student_id,
        expert_id=expert.id,
        review_token=str(uuid.uuid4()),
        goals=goals,
    )


def accept(mentorship: Mentorship) -> Mentorship:
    return mentorship.model_copy(update={"status": "accepted", "updated_at": datetime.now(timezone.utc)})


def decline(mentorship: Mentorship) -> Mentorship:
    return mentorship.model_copy(update={"status": "declined", "updated_at": datetime.now(timezone.utc)})


def complete(mentorship: Mentorship) -> Mentorship:
    return mentorship.model_copy(update={"status": "completed", "updated_at": datetime.now(timezone.utc)})


def add_note(mentorship: Mentorship, *, author_role: MentorshipNoteAuthorRole, note: str) -> Mentorship:
    new_note = MentorshipProgressNote(id=str(uuid.uuid4()), author_role=author_role, note=note)
    return mentorship.model_copy(
        update={
            "progress_notes": [*mentorship.progress_notes, new_note],
            "updated_at": datetime.now(timezone.utc),
        }
    )


def count_active_mentees(mentorships: list[Mentorship], expert_id: str) -> int:
    return sum(1 for m in mentorships if m.expert_id == expert_id and m.status == "accepted")


#: A student already has a live claim on this expert — block a second
#: request. "declined"/"completed" are resolved outcomes, not active
#: ones, so a fresh request is allowed after either.
_ACTIVE_STATUSES = {"requested", "accepted"}


def has_active_mentorship(mentorships: list[Mentorship], expert_id: str) -> bool:
    return any(m.expert_id == expert_id and m.status in _ACTIVE_STATUSES for m in mentorships)


def is_eligible_for_mentorship(expert: Mentor, current_mentee_count: int) -> bool:
    """``accepts_mentorship`` is the primary, non-negotiable gate.
    ``max_students`` is an opt-in secondary constraint: it only
    constrains capacity when explicitly set above 0, mirroring the
    exact convention ``ExpertConnectScreen.tsx`` already uses to decide
    whether a capacity figure is even meaningful to show
    (``max_students > 0``) — this is not a claim that ``max_students
    == 0`` means "unlimited," only that no explicit cap has been set,
    so only the ``accepts_mentorship`` gate applies in that case."""
    if not expert.accepts_mentorship:
        return False
    if expert.max_students > 0 and current_mentee_count >= expert.max_students:
        return False
    return True
