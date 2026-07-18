"""Responsibility: Student Experiment History — read-only queries over
StudentProfile.career_experiments."""

from aureon.domain.models.experiment import ExperimentCompletion
from aureon.domain.models.student_profile import StudentProfile


def get_experiment_history(profile: StudentProfile) -> list[ExperimentCompletion]:
    return profile.career_experiments


def get_completed_experiment_ids(profile: StudentProfile) -> set[str]:
    return {completion.experiment_id for completion in profile.career_experiments}
