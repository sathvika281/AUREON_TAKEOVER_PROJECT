from datetime import datetime, timezone

from aureon.domain.models.experiment import Experiment, ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.experience_lab_service import build_experience_lab_view

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1", title="Debug a Tiny Bug", category="debug_code", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="note", related_world="AI",
        target_traits=["analytical_thinking"], reflection_prompt="p",
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def _mission(**overrides) -> LifeMission:
    defaults = dict(
        id="mission_climate", name="Solve Climate Problems", description="d",
        related_tags=["climate", "sustainability"],
    )
    defaults.update(overrides)
    return LifeMission(**defaults)


def test_experiments_group_into_career_vs_mission_by_related_life_mission_ids():
    career_exp = _experiment(id="exp_career")
    mission_exp = _experiment(id="exp_mission", related_life_mission_ids=["mission_climate"])
    profile = StudentProfile(student_id="s1")

    view = build_experience_lab_view(
        profile, experiments=[career_exp, mission_exp], missions=[_mission()], now=NOW
    )

    assert [e.id for e in view.career_experiences] == ["exp_career"]
    assert [e.id for e in view.mission_experiences] == ["exp_mission"]


def test_emerging_missions_only_include_missions_with_real_evidence():
    mission_exp = _experiment(id="exp_mission", related_life_mission_ids=["mission_climate"])
    profile = StudentProfile(student_id="s1")

    view = build_experience_lab_view(
        profile, experiments=[mission_exp], missions=[_mission()], now=NOW
    )

    assert view.emerging_missions == []


def test_emerging_mission_pairs_with_the_right_uncompleted_suggested_experience():
    mission_exp = _experiment(id="exp_mission", related_life_mission_ids=["mission_climate"])
    other_mission_exp = _experiment(
        id="exp_mission_2", title="A second climate activity", related_life_mission_ids=["mission_climate"]
    )
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_mission", experiment_title="Analyze a climate problem",
            related_world="AI", target_traits=["analytical_thinking"], completed_at=NOW,
            evidence=ExperimentEvidence(curiosity=True),
        )
    )

    view = build_experience_lab_view(
        profile, experiments=[mission_exp, other_mission_exp], missions=[_mission()], now=NOW
    )

    assert len(view.emerging_missions) == 1
    emerging = view.emerging_missions[0]
    assert emerging.resonance.mission.id == "mission_climate"
    # exp_mission is already completed — the suggestion must skip to the other one.
    assert emerging.suggested_experience is not None
    assert emerging.suggested_experience.id == "exp_mission_2"


def test_recommended_excludes_already_completed_experiments():
    exp = _experiment(id="exp_1")
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug",
            related_world="AI", target_traits=["analytical_thinking"], completed_at=NOW,
            evidence=ExperimentEvidence(),
        )
    )

    view = build_experience_lab_view(profile, experiments=[exp], missions=[], now=NOW)

    assert view.recommended == []


def test_completed_history_matches_get_experiment_history():
    exp = _experiment(id="exp_1")
    profile = StudentProfile(student_id="s1")
    completion = ExperimentCompletion(
        id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug",
        related_world="AI", target_traits=["analytical_thinking"], completed_at=NOW,
        evidence=ExperimentEvidence(),
    )
    profile.career_experiments.append(completion)

    view = build_experience_lab_view(profile, experiments=[exp], missions=[], now=NOW)

    assert view.completed == [completion]
    assert view.completed_experiment_ids == {"exp_1"}
