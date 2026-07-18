from aureon.domain.services.mentorship_service import (
    accept,
    add_note,
    complete,
    count_active_mentees,
    decline,
    has_active_mentorship,
    is_eligible_for_mentorship,
    request_mentorship,
)

from ._connect_factories import make_expert, make_mentorship


def test_request_mentorship_always_reads_expert_identity_from_the_real_mentor_record():
    expert = make_expert(id="expert_9", name="Dr. Real Expert")
    mentorship = request_mentorship(student_id="student_1", expert=expert, goals="Learn about research careers.")

    assert mentorship.expert_id == "expert_9"
    assert mentorship.student_id == "student_1"
    assert mentorship.status == "requested"
    assert mentorship.goals == "Learn about research careers."


def test_request_mentorship_generates_unique_review_tokens():
    expert = make_expert()
    m1 = request_mentorship(student_id="s1", expert=expert, goals="x")
    m2 = request_mentorship(student_id="s1", expert=expert, goals="x")
    assert m1.review_token != m2.review_token
    assert m1.id != m2.id


def test_accept_moves_status_to_accepted():
    mentorship = make_mentorship(status="requested")
    updated = accept(mentorship)
    assert updated.status == "accepted"


def test_decline_moves_status_to_declined():
    mentorship = make_mentorship(status="requested")
    updated = decline(mentorship)
    assert updated.status == "declined"


def test_complete_moves_status_to_completed():
    mentorship = make_mentorship(status="accepted")
    updated = complete(mentorship)
    assert updated.status == "completed"


def test_add_note_appends_without_losing_existing_notes():
    mentorship = make_mentorship()
    once = add_note(mentorship, author_role="student", note="First note.")
    twice = add_note(once, author_role="expert", note="Second note.")

    assert [n.note for n in twice.progress_notes] == ["First note.", "Second note."]
    assert twice.progress_notes[1].author_role == "expert"


def test_count_active_mentees_only_counts_accepted_status_for_the_given_expert():
    mentorships = [
        make_mentorship(id="m1", expert_id="expert_1", status="accepted"),
        make_mentorship(id="m2", expert_id="expert_1", status="requested"),
        make_mentorship(id="m3", expert_id="expert_1", status="completed"),
        make_mentorship(id="m4", expert_id="expert_2", status="accepted"),
    ]
    assert count_active_mentees(mentorships, "expert_1") == 1


def test_has_active_mentorship_blocks_on_requested_or_accepted():
    for status in ("requested", "accepted"):
        mentorships = [make_mentorship(expert_id="expert_1", status=status)]
        assert has_active_mentorship(mentorships, "expert_1") is True


def test_has_active_mentorship_allows_after_declined_or_completed():
    for status in ("declined", "completed"):
        mentorships = [make_mentorship(expert_id="expert_1", status=status)]
        assert has_active_mentorship(mentorships, "expert_1") is False


def test_has_active_mentorship_ignores_other_experts():
    mentorships = [make_mentorship(expert_id="expert_2", status="accepted")]
    assert has_active_mentorship(mentorships, "expert_1") is False


def test_is_eligible_for_mentorship_blocks_when_expert_does_not_accept_mentorship_regardless_of_capacity():
    expert = make_expert(accepts_mentorship=False, max_students=0)
    assert is_eligible_for_mentorship(expert, current_mentee_count=0) is False

    expert_with_room = make_expert(accepts_mentorship=False, max_students=5)
    assert is_eligible_for_mentorship(expert_with_room, current_mentee_count=0) is False


def test_is_eligible_for_mentorship_blocks_at_or_over_an_explicit_capacity_cap():
    expert = make_expert(accepts_mentorship=True, max_students=2)
    assert is_eligible_for_mentorship(expert, current_mentee_count=2) is False
    assert is_eligible_for_mentorship(expert, current_mentee_count=3) is False


def test_is_eligible_for_mentorship_allows_under_an_explicit_capacity_cap():
    expert = make_expert(accepts_mentorship=True, max_students=2)
    assert is_eligible_for_mentorship(expert, current_mentee_count=1) is True


def test_is_eligible_for_mentorship_allows_when_no_explicit_cap_is_set():
    """max_students=0 means no explicit cap was set, not "unlimited" as
    an invented claim — it simply means the capacity constraint doesn't
    apply, matching ExpertConnectScreen.tsx's own existing convention
    for when a cap is meaningful to display at all (max_students > 0)."""
    expert = make_expert(accepts_mentorship=True, max_students=0)
    assert is_eligible_for_mentorship(expert, current_mentee_count=50) is True
