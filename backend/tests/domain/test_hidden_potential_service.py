from datetime import datetime, timezone

from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.experiment import Experiment, ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.hidden_potential import build_hidden_potential_response
from aureon.domain.services.progressive_discovery import get_progressive_discovery_state
from aureon.domain.services.talent_pattern_engine import analyze_talents

NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1", title="Debug a Tiny Bug", category="debug_code", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="note", related_world="AI",
        target_traits=["persistence"], reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def _completion(**overrides) -> ExperimentCompletion:
    defaults = dict(
        id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug", related_world="AI",
        target_traits=["persistence"], completed_at=NOW, evidence=ExperimentEvidence(persistence=True),
    )
    defaults.update(overrides)
    return ExperimentCompletion(**defaults)


def test_empty_profile_yields_empty_response():
    profile = StudentProfile(student_id="s1")

    response = build_hidden_potential_response(profile, experiments=[])

    assert response.hidden_patterns == []
    assert response.strengths.emerging == []
    assert response.strengths.growing == []
    assert response.strengths.consistently_observed == []
    assert response.evidence_timeline == []
    assert response.suggested_experience is None
    assert response.discovery_statistics.traits_tracked == 0


def test_strengths_bucketing_matches_analyze_talents_exactly():
    """No duplicate computation — the tier grouping must be a pure
    regrouping of analyze_talents' own output, never a re-derivation."""
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(_completion())
    profile.career_experiments.append(_completion(id="c2"))

    response = build_hidden_potential_response(profile, experiments=[])
    real_patterns = analyze_talents(profile)

    real_by_tier = {"still_discovering": [], "emerging": [], "growing": []}
    for p in real_patterns:
        real_by_tier[p.tier].append(p.talent)

    assert [p.talent for p in response.strengths.emerging] == real_by_tier["still_discovering"]
    assert [p.talent for p in response.strengths.growing] == real_by_tier["emerging"]
    assert [p.talent for p in response.strengths.consistently_observed] == real_by_tier["growing"]


def test_suggested_experience_matches_progressive_discovery_exactly():
    """No second recommendation engine — must be byte-identical to what
    Progressive Discovery alone would compute."""
    profile = StudentProfile(student_id="s1")
    catalog = [_experiment(id="exp_1"), _experiment(id="exp_2", title="Second")]

    response = build_hidden_potential_response(profile, experiments=catalog)
    expected = get_progressive_discovery_state(profile, mode="exploration", experiments=catalog).suggested_experiment

    assert response.suggested_experience == expected
    assert response.suggested_experience.id == "exp_1"


def test_discovery_statistics_are_real_counts():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["persistence"] = TraitSignal(score=0.7, summary="Strong.")
    profile.career_dna.traits["creativity"] = TraitSignal(score=0.1, summary="Weak.")
    profile.career_experiments.append(_completion())

    response = build_hidden_potential_response(profile, experiments=[])

    assert response.discovery_statistics.traits_tracked == 2
    assert response.discovery_statistics.traits_with_strong_evidence == 1
    assert response.discovery_statistics.experiments_completed == 1


def test_evidence_timeline_is_flattened_and_sorted_descending():
    profile = StudentProfile(student_id="s1")
    older = _completion(id="c1", completed_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    newer = _completion(id="c2", completed_at=datetime(2025, 6, 1, tzinfo=timezone.utc))
    profile.career_experiments.append(older)
    profile.career_experiments.append(newer)

    response = build_hidden_potential_response(profile, experiments=[])

    assert len(response.evidence_timeline) == 2
    assert response.evidence_timeline[0].observed_at > response.evidence_timeline[1].observed_at
    assert all(item.talent == "persistence" for item in response.evidence_timeline)


def test_hidden_patterns_reuse_the_existing_pairwise_engine_unmodified():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["analytical_thinking"] = TraitSignal(score=0.6, summary="")
    profile.career_dna.traits["creativity"] = TraitSignal(score=0.6, summary="")

    response = build_hidden_potential_response(profile, experiments=[])

    assert len(response.hidden_patterns) == 1
    assert response.hidden_patterns[0].id == "analytical_thinking-creativity"
