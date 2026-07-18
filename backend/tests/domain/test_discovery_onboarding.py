from datetime import datetime, timezone

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.discovery_onboarding import complete_onboarding

NOW = datetime.now(timezone.utc)


def _complete(profile: StudentProfile, **overrides) -> None:
    defaults: dict = dict(
        name="Alex", age=17, stage="College", location_state="Karnataka", location_city="Bengaluru",
        preferred_language="English", current_situation="few_careers", worlds=["AI"], worlds_unsure=False, now=NOW,
    )
    defaults.update(overrides)
    complete_onboarding(profile, **defaults)


def test_complete_onboarding_persists_all_real_answers():
    profile = StudentProfile(student_id="s1")
    _complete(profile)

    onboarding = profile.discovery_onboarding
    assert onboarding.completed is True
    assert onboarding.completed_at == NOW
    assert onboarding.name == "Alex"
    assert onboarding.age == 17
    assert onboarding.stage == "College"
    assert onboarding.location_state == "Karnataka"
    assert onboarding.location_city == "Bengaluru"
    assert onboarding.preferred_language == "English"
    assert onboarding.current_situation == "few_careers"


def test_complete_onboarding_creates_one_world_signal_per_selected_world_and_queues_followups():
    profile = StudentProfile(student_id="s1")
    _complete(profile, worlds=["AI", "Biology"])

    onboarding = profile.discovery_onboarding
    assert {s.world for s in onboarding.world_signals} == {"AI", "Biology"}
    assert onboarding.worlds_pending_followup == ["AI", "Biology"]


def test_complete_onboarding_maps_stage_onto_the_existing_academic_level_field():
    profile = StudentProfile(student_id="s1")
    _complete(profile, stage="School")
    assert profile.foundation_memory.identity.academic_level == "high_school"

    profile2 = StudentProfile(student_id="s2")
    _complete(profile2, stage="Professional")
    assert profile2.foundation_memory.identity.academic_level == "graduate"


def test_complete_onboarding_records_uncertainty_for_no_idea_situation():
    profile = StudentProfile(student_id="s1")
    _complete(profile, current_situation="no_idea", worlds=[])

    contexts = [s.context for s in profile.discovery_onboarding.uncertainty_signals]
    assert "no_idea" in contexts


def test_complete_onboarding_records_uncertainty_for_worlds_unsure():
    profile = StudentProfile(student_id="s1")
    _complete(profile, worlds=[], worlds_unsure=True)

    contexts = [s.context for s in profile.discovery_onboarding.uncertainty_signals]
    assert "worlds_unsure" in contexts


def test_complete_onboarding_with_no_stage_leaves_academic_level_untouched():
    profile = StudentProfile(student_id="s1")
    _complete(profile, stage=None)
    assert profile.foundation_memory.identity.academic_level is None
