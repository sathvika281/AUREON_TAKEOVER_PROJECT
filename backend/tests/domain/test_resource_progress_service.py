from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.resource_progress_service import (
    list_progress_for_circle,
    toggle_bookmark,
    toggle_completed,
)


def _profile() -> StudentProfile:
    return StudentProfile(student_id="student_1")


def test_toggle_bookmark_adds_then_removes_idempotently():
    profile = _profile()

    toggle_bookmark(profile, circle_id="circle_1", resource_type="books", resource_label="A Real Book")
    assert len(profile.circle_resource_progress) == 1
    assert profile.circle_resource_progress[0].status == "bookmarked"

    toggle_bookmark(profile, circle_id="circle_1", resource_type="books", resource_label="A Real Book")
    assert profile.circle_resource_progress == []


def test_bookmark_and_completed_are_independent_states_for_the_same_resource():
    profile = _profile()

    toggle_bookmark(profile, circle_id="circle_1", resource_type="books", resource_label="A Real Book")
    toggle_completed(profile, circle_id="circle_1", resource_type="books", resource_label="A Real Book")

    statuses = {e.status for e in profile.circle_resource_progress}
    assert statuses == {"bookmarked", "completed"}


def test_list_progress_for_circle_filters_by_circle_id():
    profile = _profile()
    toggle_bookmark(profile, circle_id="circle_1", resource_type="books", resource_label="Book A")
    toggle_bookmark(profile, circle_id="circle_2", resource_type="books", resource_label="Book B")

    results = list_progress_for_circle(profile, "circle_1")
    assert len(results) == 1
    assert results[0].resource_label == "Book A"


def test_toggle_completed_distinguishes_resources_by_composite_key():
    profile = _profile()
    toggle_completed(profile, circle_id="circle_1", resource_type="books", resource_label="Book A")
    toggle_completed(profile, circle_id="circle_1", resource_type="podcasts", resource_label="Book A")

    assert len(profile.circle_resource_progress) == 2
