import uuid
from datetime import datetime, timezone

from aureon.domain.models.career_experience import EventRegistration, ExpertSessionBooking, GuidanceRequest
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile

"""Pure, testable Expert Connect actions (V13) — extracted from
api/v1/career_experience.py's route bodies so the real behavior (never
trusting client-supplied names, idempotent save/unsave, deduped event
registration) is unit-testable without a live Supabase connection."""


def add_expert_session_booking(
    profile: StudentProfile, mentor: Mentor, *, slot_start: datetime, topic: str
) -> ExpertSessionBooking:
    """A real, student-initiated request — never auto-accepted. The
    mentor's name is always read from the real Mentor record, never
    trusted from client input."""
    booking = ExpertSessionBooking(
        id=str(uuid.uuid4()), mentor_id=mentor.id, mentor_name=mentor.name,
        slot_start=slot_start, topic=topic, created_at=datetime.now(timezone.utc),
    )
    profile.expert_session_bookings.append(booking)
    profile.updated_at = datetime.now(timezone.utc)
    return booking


def add_guidance_request(profile: StudentProfile, mentor: Mentor, *, message: str) -> GuidanceRequest:
    request = GuidanceRequest(
        id=str(uuid.uuid4()), mentor_id=mentor.id, mentor_name=mentor.name,
        message=message, created_at=datetime.now(timezone.utc),
    )
    profile.guidance_requests.append(request)
    profile.updated_at = datetime.now(timezone.utc)
    return request


def save_expert(profile: StudentProfile, mentor_id: str) -> list[str]:
    """Idempotent — saving an already-saved expert never creates a
    duplicate entry."""
    if mentor_id not in profile.saved_experts:
        profile.saved_experts.append(mentor_id)
        profile.updated_at = datetime.now(timezone.utc)
    return profile.saved_experts


def unsave_expert(profile: StudentProfile, mentor_id: str) -> list[str]:
    if mentor_id in profile.saved_experts:
        profile.saved_experts.remove(mentor_id)
        profile.updated_at = datetime.now(timezone.utc)
    return profile.saved_experts


def add_event_registration(profile: StudentProfile, *, event_id: str, event_title: str) -> EventRegistration | None:
    """Deduped by event_id — registering twice for the same real event
    never creates a second record; returns ``None`` when already
    registered so the caller can tell the two cases apart."""
    if any(r.event_id == event_id for r in profile.event_registrations):
        return None
    registration = EventRegistration(
        id=str(uuid.uuid4()), event_id=event_id, event_title=event_title,
        created_at=datetime.now(timezone.utc),
    )
    profile.event_registrations.append(registration)
    profile.updated_at = datetime.now(timezone.utc)
    return registration
