from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment, ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.discovery_onboarding import complete_onboarding
from aureon.domain.services.progressive_discovery import WORLD_FOLLOWUPS, get_progressive_discovery_state

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1", title="Debug a Tiny Bug", category="debug_code", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="note", related_world="AI",
        target_traits=["analytical_thinking"], reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def test_world_followups_cover_every_onboarding_world_and_always_offer_none_yet():
    for world in ("AI", "Space", "Healthcare", "Business", "Design", "Arts", "Psychology"):
        assert world in WORLD_FOLLOWUPS
        assert "None Yet" in WORLD_FOLLOWUPS[world].options


def test_state_reflects_onboarding_not_completed_before_onboarding():
    profile = StudentProfile(student_id="s1")
    state = get_progressive_discovery_state(profile, mode="exploration")

    assert state.onboarding_completed is False
    assert state.pending_curiosity_checkin is None
    assert state.world_signals == []
    assert state.orbit_status is not None  # Orbit Status never depends on onboarding


def test_state_reflects_a_real_pending_checkin_after_onboarding():
    profile = StudentProfile(student_id="s1")
    complete_onboarding(
        profile, name="Alex", age=17, stage="College", location_state="Karnataka",
        location_city="Bengaluru", preferred_language="English", current_situation="few_careers",
        worlds=["AI", "Space"], worlds_unsure=False, now=NOW,
    )

    state = get_progressive_discovery_state(profile, mode="exploration")

    assert state.onboarding_completed is True
    assert state.pending_curiosity_checkin is not None
    assert state.pending_curiosity_checkin.world == "AI"
    assert state.pending_curiosity_checkin.options == WORLD_FOLLOWUPS["AI"].options
    assert len(state.world_signals) == 2


def test_state_has_no_pending_checkin_when_queue_is_exhausted():
    profile = StudentProfile(student_id="s1")
    complete_onboarding(
        profile, name=None, age=None, stage=None, location_state=None, location_city=None,
        preferred_language=None, current_situation=None, worlds=[], worlds_unsure=True, now=NOW,
    )

    state = get_progressive_discovery_state(profile, mode="exploration")
    assert state.pending_curiosity_checkin is None


def test_suggested_experiment_is_none_when_catalog_omitted():
    """Backward compatibility — every pre-Discover-Batch-2 call site
    behaves exactly as before."""
    profile = StudentProfile(student_id="s1")

    state = get_progressive_discovery_state(profile, mode="exploration")

    assert state.suggested_experiment is None


def test_suggested_experiment_is_the_first_uncompleted_one():
    profile = StudentProfile(student_id="s1")
    catalog = [_experiment(id="exp_1", title="First"), _experiment(id="exp_2", title="Second")]

    state = get_progressive_discovery_state(profile, mode="exploration", experiments=catalog)

    assert state.suggested_experiment is not None
    assert state.suggested_experiment.id == "exp_1"


def test_suggested_experiment_skips_already_completed_ones():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="First", related_world="AI",
            target_traits=[], completed_at=NOW, evidence=ExperimentEvidence(),
        )
    )
    catalog = [_experiment(id="exp_1", title="First"), _experiment(id="exp_2", title="Second")]

    state = get_progressive_discovery_state(profile, mode="exploration", experiments=catalog)

    assert state.suggested_experiment.id == "exp_2"


def test_suggested_experiment_honestly_none_once_everything_tried():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="First", related_world="AI",
            target_traits=[], completed_at=NOW, evidence=ExperimentEvidence(),
        )
    )
    catalog = [_experiment(id="exp_1", title="First")]

    state = get_progressive_discovery_state(profile, mode="exploration", experiments=catalog)

    assert state.suggested_experiment is None
