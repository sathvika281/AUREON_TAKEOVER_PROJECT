from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_result import complete_experiment
from aureon.domain.services.world_signal import create_world_signal

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1",
        title="Debug a Tiny Bug",
        category="debug_code",
        description="d",
        instructions="i",
        estimated_minutes=10,
        age_appropriate_note="note",
        related_world="AI",
        target_traits=["analytical_thinking", "persistence"],
        reflection_prompt="p",
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def test_completion_is_appended_to_profile_history():
    profile = StudentProfile(student_id="s1")
    experiment = _experiment()

    completion = complete_experiment(profile, experiment, evidence=ExperimentEvidence(enjoyment=True), now=NOW)

    assert profile.career_experiments == [completion]
    assert completion.experiment_title == experiment.title
    assert completion.related_world == experiment.related_world
    assert completion.target_traits == experiment.target_traits


def test_creates_and_reinforces_world_signal_when_none_exists():
    profile = StudentProfile(student_id="s1")
    experiment = _experiment(related_world="Space")

    complete_experiment(profile, experiment, evidence=ExperimentEvidence(curiosity=True), now=NOW)

    signal = next(s for s in profile.discovery_onboarding.world_signals if s.world == "Space")
    assert signal.status == "reinforced"
    assert signal.confidence > 0.3  # INITIAL_CONFIDENCE, then reinforced up
    assert any("Debug a Tiny Bug" in item or "curiosity" in item for item in signal.evidence)


def test_reinforces_existing_world_signal_instead_of_duplicating():
    profile = StudentProfile(student_id="s1")
    profile.discovery_onboarding.world_signals.append(create_world_signal("AI", NOW))
    experiment = _experiment(related_world="AI")

    complete_experiment(profile, experiment, evidence=ExperimentEvidence(persistence=True), now=NOW)

    ai_signals = [s for s in profile.discovery_onboarding.world_signals if s.world == "AI"]
    assert len(ai_signals) == 1
    assert ai_signals[0].confidence > 0.3


def test_writes_evidence_graph_entries_for_each_target_trait():
    profile = StudentProfile(student_id="s1")
    experiment = _experiment(target_traits=["analytical_thinking", "persistence"])

    complete_experiment(profile, experiment, evidence=ExperimentEvidence(persistence=True), now=NOW)

    traits_covered = {e.related_trait for e in profile.evidence_graph}
    assert traits_covered == {"analytical_thinking", "persistence"}
    for record in profile.evidence_graph:
        assert record.source == "experiment"
        assert record.relation == "supports"


def test_completion_with_no_reported_flags_still_records_real_evidence():
    profile = StudentProfile(student_id="s1")
    experiment = _experiment(target_traits=["analytical_thinking"])

    complete_experiment(profile, experiment, evidence=ExperimentEvidence(), now=NOW)

    assert len(profile.evidence_graph) == 1
    assert "Debug a Tiny Bug" in profile.evidence_graph[0].text
