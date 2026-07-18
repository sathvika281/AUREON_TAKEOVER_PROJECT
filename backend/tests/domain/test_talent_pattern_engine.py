from datetime import datetime, timezone

from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.experiment import ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.talent_pattern_engine import TALENT_NAMES, analyze_talents

NOW = datetime.now(timezone.utc)


def _completion(target_traits: list[str], **evidence_flags) -> ExperimentCompletion:
    return ExperimentCompletion(
        id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug", related_world="AI",
        target_traits=target_traits, completed_at=NOW, evidence=ExperimentEvidence(**evidence_flags),
    )


def test_zero_evidence_talent_produces_no_card():
    profile = StudentProfile(student_id="s1")

    patterns = analyze_talents(profile)

    assert patterns == []


def test_talent_names_are_a_fixed_real_vocabulary():
    assert TALENT_NAMES == (
        "analytical_thinking", "creativity", "communication", "persistence", "empathy", "systems_thinking"
    )


def test_single_source_evidence_yields_still_discovering():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(_completion(["persistence"], persistence=True))

    patterns = analyze_talents(profile)

    persistence = next(p for p in patterns if p.talent == "persistence")
    assert persistence.tier == "still_discovering"
    assert len(persistence.evidence) == 1
    assert persistence.evidence[0].source == "experiment"


def test_two_same_source_items_yield_emerging():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(_completion(["persistence"], persistence=True))
    profile.career_experiments.append(_completion(["persistence"], persistence=True))

    patterns = analyze_talents(profile)

    persistence = next(p for p in patterns if p.talent == "persistence")
    assert persistence.tier == "emerging"


def test_three_items_across_two_sources_yield_growing():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["analytical_thinking"] = TraitSignal(score=0.7, summary="Strong logical reasoning.")
    profile.career_experiments.append(_completion(["analytical_thinking"], curiosity=True))
    profile.career_experiments.append(_completion(["analytical_thinking"], confidence=True))

    patterns = analyze_talents(profile)

    analytical = next(p for p in patterns if p.talent == "analytical_thinking")
    assert analytical.tier == "growing"
    sources = {e.source for e in analytical.evidence}
    assert sources == {"career_dna", "experiment"}


def test_three_same_source_items_without_diversity_stay_emerging():
    profile = StudentProfile(student_id="s1")
    for _ in range(3):
        profile.career_experiments.append(_completion(["persistence"], persistence=True))

    patterns = analyze_talents(profile)

    persistence = next(p for p in patterns if p.talent == "persistence")
    assert persistence.tier == "emerging"  # 3 items but only 1 source type — not "growing"


def test_weak_career_dna_score_is_not_counted_as_evidence():
    profile = StudentProfile(student_id="s1")
    profile.career_dna.traits["creativity"] = TraitSignal(score=0.2, summary="Not much shown yet.")

    patterns = analyze_talents(profile)

    assert all(p.talent != "creativity" for p in patterns)


def test_reflection_keyword_match_counts_as_real_evidence():
    profile = StudentProfile(student_id="s1")
    profile.reflection_journal.append(
        ReflectionEntry(
            prompt="How did that feel?",
            response="I kept trying even when the first two attempts failed.",
            created_at=NOW, answered_at=NOW,
        )
    )

    patterns = analyze_talents(profile)

    persistence = next(p for p in patterns if p.talent == "persistence")
    assert persistence.tier == "still_discovering"
    assert persistence.evidence[0].source == "reflection"


def test_every_pattern_explanation_cites_something_real():
    profile = StudentProfile(student_id="s1")
    profile.career_experiments.append(_completion(["persistence"], persistence=True))
    profile.career_experiments.append(_completion(["persistence"], persistence=True))

    patterns = analyze_talents(profile)

    for pattern in patterns:
        assert pattern.explanation
        assert "%" not in pattern.explanation  # never a percentage/score
