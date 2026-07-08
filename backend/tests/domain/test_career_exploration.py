from datetime import datetime, timedelta, timezone

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.career_exploration import (
    DEDUP_WINDOW_SECONDS,
    record_exploration_event,
)

NOW = datetime.now(timezone.utc)


def test_records_a_new_event():
    profile = StudentProfile(student_id="s1")
    event = record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=NOW,
    )
    assert event is not None
    assert len(profile.career_exploration_history) == 1
    assert profile.career_exploration_history[0].interaction_type == "opened"


def test_opened_is_auto_upgraded_to_revisited_on_a_later_visit():
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=NOW,
    )
    later = NOW + timedelta(minutes=10)
    event = record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=later,
    )
    assert event is not None
    assert event.interaction_type == "revisited"
    assert len(profile.career_exploration_history) == 2


def test_rapid_double_fire_of_opened_is_deduped_even_across_the_revisited_boundary():
    """Regression test: a rapid double-fire of "opened" for a career that
    was already visited earlier upgrades to "revisited" — the second,
    near-instant call must still be deduped against that upgrade, not
    treated as a distinct event just because its label differs."""
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=NOW,
    )
    much_later = NOW + timedelta(minutes=10)
    first_revisit = record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=much_later,
    )
    assert first_revisit is not None
    assert first_revisit.interaction_type == "revisited"

    near_instant_after = much_later + timedelta(seconds=1)
    duplicate = record_exploration_event(
        profile, career_id="physician_general", interaction_type="opened",
        metadata={}, now=near_instant_after,
    )
    assert duplicate is None
    assert len(profile.career_exploration_history) == 2


def test_near_instant_duplicate_is_skipped():
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="bookmarked",
        metadata={}, now=NOW,
    )
    just_after = NOW + timedelta(seconds=DEDUP_WINDOW_SECONDS - 1)
    event = record_exploration_event(
        profile, career_id="physician_general", interaction_type="bookmarked",
        metadata={}, now=just_after,
    )
    assert event is None
    assert len(profile.career_exploration_history) == 1


def test_genuine_repeat_outside_dedup_window_is_recorded():
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="future_lens_explored",
        metadata={}, now=NOW,
    )
    much_later = NOW + timedelta(seconds=DEDUP_WINDOW_SECONDS + 1)
    event = record_exploration_event(
        profile, career_id="physician_general", interaction_type="future_lens_explored",
        metadata={}, now=much_later,
    )
    assert event is not None
    assert len(profile.career_exploration_history) == 2


def test_dedup_does_not_cross_interaction_types_or_careers():
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="bookmarked",
        metadata={}, now=NOW,
    )
    # Same career, different interaction type — not a duplicate.
    event_a = record_exploration_event(
        profile, career_id="physician_general", interaction_type="story_viewed",
        metadata={}, now=NOW,
    )
    # Different career, same interaction type — not a duplicate.
    event_b = record_exploration_event(
        profile, career_id="civil_engineer", interaction_type="bookmarked",
        metadata={}, now=NOW,
    )
    assert event_a is not None
    assert event_b is not None
    assert len(profile.career_exploration_history) == 3


def test_metadata_is_preserved():
    profile = StudentProfile(student_id="s1")
    record_exploration_event(
        profile, career_id="physician_general", interaction_type="compared",
        metadata={"compared_with": "civil_engineer"}, now=NOW,
    )
    assert profile.career_exploration_history[0].metadata == {"compared_with": "civil_engineer"}
