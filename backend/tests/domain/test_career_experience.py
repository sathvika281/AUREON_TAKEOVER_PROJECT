from datetime import datetime, timezone

from aureon.domain.models.mentor import Mentor
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.career_experience_actions import (
    add_event_registration,
    add_expert_session_booking,
    add_guidance_request,
    save_expert,
    unsave_expert,
)

MENTOR = Mentor(
    id="mentor_real", name="Dr. Real Mentor", role_type="professor", field="x", bio="x", learning_style_fit="x",
)


def _profile() -> StudentProfile:
    return StudentProfile(student_id="s1")


def test_booking_persists_the_real_mentor_name_not_client_input():
    profile = _profile()
    slot = datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc)

    booking = add_expert_session_booking(profile, MENTOR, slot_start=slot, topic="Career advice")

    assert len(profile.expert_session_bookings) == 1
    assert profile.expert_session_bookings[0].mentor_name == "Dr. Real Mentor"
    assert profile.expert_session_bookings[0].slot_start == slot
    assert booking.topic == "Career advice"


def test_multiple_bookings_are_append_only():
    profile = _profile()
    slot = datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc)
    add_expert_session_booking(profile, MENTOR, slot_start=slot, topic="First")
    add_expert_session_booking(profile, MENTOR, slot_start=slot, topic="Second")

    assert len(profile.expert_session_bookings) == 2


def test_guidance_request_persists_real_mentor_name():
    profile = _profile()
    request = add_guidance_request(profile, MENTOR, message="Can you help me think through this?")

    assert len(profile.guidance_requests) == 1
    assert request.mentor_name == "Dr. Real Mentor"
    assert request.status == "requested"


def test_save_expert_is_idempotent():
    profile = _profile()
    save_expert(profile, "mentor_real")
    save_expert(profile, "mentor_real")

    assert profile.saved_experts == ["mentor_real"]


def test_unsave_expert_removes_and_is_safe_when_not_saved():
    profile = _profile()
    save_expert(profile, "mentor_real")
    unsave_expert(profile, "mentor_real")
    unsave_expert(profile, "mentor_real")  # never raises

    assert profile.saved_experts == []


def test_event_registration_is_deduped_by_event_id():
    profile = _profile()
    first = add_event_registration(profile, event_id="event_1", event_title="NIAT Build Sprint Hackathon")
    second = add_event_registration(profile, event_id="event_1", event_title="NIAT Build Sprint Hackathon")

    assert first is not None
    assert second is None
    assert len(profile.event_registrations) == 1
    assert profile.event_registrations[0].event_title == "NIAT Build Sprint Hackathon"
