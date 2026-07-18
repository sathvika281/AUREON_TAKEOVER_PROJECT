from datetime import datetime, timezone

from aureon.domain.models.experiment import ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experiment_history import get_completed_experiment_ids, get_experiment_history

NOW = datetime.now(timezone.utc)


def test_empty_history_for_new_student():
    profile = StudentProfile(student_id="s1")

    assert get_experiment_history(profile) == []
    assert get_completed_experiment_ids(profile) == set()


def test_history_reflects_real_completions():
    profile = StudentProfile(student_id="s1")
    completion = ExperimentCompletion(
        id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug", related_world="AI",
        target_traits=["analytical_thinking"], completed_at=NOW, evidence=ExperimentEvidence(),
    )
    profile.career_experiments.append(completion)

    assert get_experiment_history(profile) == [completion]
    assert get_completed_experiment_ids(profile) == {"exp_1"}
