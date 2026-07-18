from datetime import datetime, timedelta, timezone

from aureon.domain.models.discovery_onboarding import DiscoveryOnboarding
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.world_signal import (
    answer_world_followup,
    create_world_signal,
    next_pending_world_followup,
    queue_world_for_followup,
    reinforce_world_signal,
)

NOW = datetime.now(timezone.utc)


def test_create_world_signal_starts_curious_with_weak_initial_confidence():
    signal = create_world_signal("AI", NOW)
    assert signal.confidence == 0.3
    assert signal.status == "curious"
    assert signal.evidence == ["selected_at_onboarding"]
    assert signal.first_observed == NOW
    assert signal.last_reinforced == NOW


def test_reinforce_with_real_evidence_increases_confidence_and_becomes_reinforced():
    signal = create_world_signal("AI", NOW)
    later = NOW + timedelta(days=3)

    reinforced = reinforce_world_signal(signal, ["Python", "Robotics"], later)

    assert reinforced.confidence == 0.5
    assert reinforced.status == "reinforced"
    assert reinforced.evidence == ["selected_at_onboarding", "Python", "Robotics"]
    assert reinforced.last_reinforced == later
    assert reinforced.first_observed == NOW  # never reset


def test_reinforce_with_only_none_yet_does_not_increase_confidence_or_status():
    signal = create_world_signal("AI", NOW)
    later = NOW + timedelta(days=3)

    reinforced = reinforce_world_signal(signal, ["None Yet"], later)

    assert reinforced.confidence == 0.3
    assert reinforced.status == "curious"
    assert reinforced.evidence == ["selected_at_onboarding", "None Yet"]
    assert reinforced.last_reinforced == later  # still updates — a real interaction happened


def test_confidence_is_capped_at_one():
    signal = create_world_signal("AI", NOW)
    for _ in range(10):
        signal = reinforce_world_signal(signal, ["Python"], NOW)
    assert signal.confidence == 1.0


def test_next_pending_world_followup_returns_first_in_queue_order():
    onboarding = DiscoveryOnboarding(worlds_pending_followup=["AI", "Biology"])
    assert next_pending_world_followup(onboarding) == "AI"


def test_next_pending_world_followup_returns_none_when_queue_empty():
    assert next_pending_world_followup(DiscoveryOnboarding()) is None


def test_answer_world_followup_reinforces_the_matching_signal_and_advances_queue():
    profile = StudentProfile(student_id="s1")
    profile.discovery_onboarding = DiscoveryOnboarding(
        world_signals=[create_world_signal("AI", NOW), create_world_signal("Biology", NOW)],
        worlds_pending_followup=["AI", "Biology"],
    )

    answer_world_followup(profile, world="AI", chosen_options=["Python"], now=NOW + timedelta(days=1))

    ai_signal = next(s for s in profile.discovery_onboarding.world_signals if s.world == "AI")
    assert ai_signal.confidence == 0.5
    assert profile.discovery_onboarding.worlds_pending_followup == ["Biology"]
    assert profile.discovery_onboarding.uncertainty_signals == []


def test_answer_world_followup_with_only_none_yet_records_an_uncertainty_signal():
    profile = StudentProfile(student_id="s1")
    profile.discovery_onboarding = DiscoveryOnboarding(
        world_signals=[create_world_signal("AI", NOW)],
        worlds_pending_followup=["AI"],
    )

    answer_world_followup(profile, world="AI", chosen_options=["None Yet"], now=NOW)

    assert len(profile.discovery_onboarding.uncertainty_signals) == 1
    assert profile.discovery_onboarding.uncertainty_signals[0].context == "none_yet:AI"


def test_queue_world_for_followup_creates_a_fresh_signal_for_a_world_not_selected_at_onboarding():
    profile = StudentProfile(student_id="s1")

    queue_world_for_followup(profile, "Space", NOW)

    assert profile.discovery_onboarding.worlds_pending_followup == ["Space"]
    assert profile.discovery_onboarding.world_signals[0].world == "Space"


def test_queue_world_for_followup_is_idempotent_for_an_already_tracked_world():
    profile = StudentProfile(student_id="s1")
    queue_world_for_followup(profile, "Space", NOW)
    queue_world_for_followup(profile, "Space", NOW)

    assert len(profile.discovery_onboarding.world_signals) == 1
    assert profile.discovery_onboarding.worlds_pending_followup == ["Space"]
