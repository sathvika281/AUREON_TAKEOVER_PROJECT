from datetime import datetime, timezone

from aureon.domain.services.shared_session_service import (
    build_note,
    complete,
    create_invite,
    join_as_participant,
    schedule,
)

from ._connect_factories import make_expert, make_shared_session


def test_create_invite_always_reads_mentor_identity_from_the_real_mentor_record():
    mentor = make_expert(id="expert_9", name="Dr. Real Expert")
    session = create_invite(student_id="student_1", mentor=mentor, career_id="c1", topic="Exploring careers")

    assert session.mentor_id == "expert_9"
    assert session.student_id == "student_1"
    assert session.status == "invited"


def test_create_invite_generates_unique_access_tokens():
    mentor = make_expert()
    session_a = create_invite(student_id="s1", mentor=mentor, career_id=None, topic="x")
    session_b = create_invite(student_id="s1", mentor=mentor, career_id=None, topic="x")

    assert session_a.access_token != session_b.access_token
    assert session_a.id != session_b.id


def test_join_as_participant_records_the_generic_participant_label():
    session = make_shared_session(participant_label="")
    updated = join_as_participant(session, participant_label="Mom")
    assert updated.participant_label == "Mom"


def test_schedule_moves_session_to_scheduled_status():
    session = make_shared_session(status="invited")
    slot = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)

    updated = schedule(session, slot=slot)

    assert updated.status == "scheduled"
    assert updated.scheduled_slot == slot


def test_complete_moves_session_to_completed_status():
    session = make_shared_session(status="scheduled")
    updated = complete(session)
    assert updated.status == "completed"


def test_build_note_uses_the_generic_participant_role_not_parent():
    note = build_note("session_1", author_role="participant", note="A real note.")
    assert note.author_role == "participant"
    assert note.session_id == "session_1"
