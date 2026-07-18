from datetime import datetime, timezone

from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.experiment import Experiment, ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.learning_style import LearningStyle
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentEvidenceItem, TalentPattern
from aureon.domain.services.learning_style_evidence import build_evidence

NOW = datetime.now(timezone.utc)


def _style(**overrides) -> LearningStyle:
    defaults = dict(id="style_visual", name="Visual", description="d", keywords=["visual", "diagram"])
    defaults.update(overrides)
    return LearningStyle(**defaults)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1", title="Observe a Design", category="observe_design", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="n", related_world="Design", target_traits=["creativity"],
        reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def test_direct_learning_style_trait_is_used_when_it_matches():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["learning_style"] = TraitSignal(score=None, summary="Prefers visual diagrams over text")
    style = _style()

    evidence = build_evidence(style, profile, [], [])

    assert any(e.source == "career_dna" for e in evidence)


def test_experiment_completion_matched_via_catalog_category():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_1", experiment_title="Observe a Design", related_world="Design",
            target_traits=["creativity"], completed_at=NOW, evidence=ExperimentEvidence(enjoyment=True),
        )
    )
    style = _style()
    catalog = [_experiment()]

    evidence = build_evidence(style, profile, [], catalog)

    assert any(e.source == "experiment" for e in evidence)


def test_experiment_completion_with_unknown_experiment_id_is_skipped():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(
        ExperimentCompletion(
            id="c1", experiment_id="exp_missing", experiment_title="Ghost", related_world="Design",
            target_traits=[], completed_at=NOW, evidence=ExperimentEvidence(),
        )
    )
    style = _style()

    evidence = build_evidence(style, profile, [], [])

    assert evidence == []


def test_talent_pattern_contributes_via_static_mapping():
    profile = StudentProfile(student_id="s1")
    style = _style(name="Exploratory", keywords=["explore"])
    talent_patterns = [
        TalentPattern(
            talent="creativity", tier="growing", explanation="e",
            evidence=[TalentEvidenceItem(source="experiment", description="d", observed_at=NOW)],
        )
    ]

    evidence = build_evidence(style, profile, talent_patterns, [])

    assert any(e.source == "hidden_potential" for e in evidence)
