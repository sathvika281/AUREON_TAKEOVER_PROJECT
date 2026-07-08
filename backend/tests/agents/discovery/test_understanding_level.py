from aureon.agents.specialized.discovery.understanding_level import derive_understanding_level
from aureon.domain.models.career_dna import CareerDNA, TraitSignal
from aureon.domain.models.career_hypothesis import CareerHypothesis


def test_seed_when_nothing_yet():
    stage, _ = derive_understanding_level(
        career_dna=CareerDNA(), hypotheses=[], mode="exploration", has_hidden_potential=False
    )
    assert stage == "Seed"


def test_explorer_with_one_trait():
    dna = CareerDNA(traits={"curiosity": TraitSignal(score=0.4, summary="curious")})
    stage, _ = derive_understanding_level(
        career_dna=dna, hypotheses=[], mode="exploration", has_hidden_potential=False
    )
    assert stage == "Explorer"


def test_patterns_emerging_when_hidden_potential_present():
    dna = CareerDNA(traits={"curiosity": TraitSignal(score=0.6, summary="curious")})
    stage, _ = derive_understanding_level(
        career_dna=dna, hypotheses=[], mode="exploration", has_hidden_potential=True
    )
    assert stage == "Patterns Emerging"


def test_identity_taking_shape_with_three_traits():
    dna = CareerDNA(
        traits={
            "curiosity": TraitSignal(score=0.4, summary="a"),
            "creativity": TraitSignal(score=0.4, summary="b"),
            "leadership": TraitSignal(score=0.4, summary="c"),
        }
    )
    stage, _ = derive_understanding_level(
        career_dna=dna, hypotheses=[], mode="exploration", has_hidden_potential=False
    )
    assert stage == "Identity Taking Shape"


def test_career_dna_forming_once_a_hypothesis_exists():
    dna = CareerDNA(traits={"curiosity": TraitSignal(score=0.4, summary="a")})
    hypotheses = [CareerHypothesis(career_name="AI Research", confidence=0.3, status="growing")]
    stage, _ = derive_understanding_level(
        career_dna=dna, hypotheses=hypotheses, mode="exploration", has_hidden_potential=False
    )
    assert stage == "Career DNA Forming"


def test_discarded_hypotheses_do_not_count_toward_career_dna_forming():
    hypotheses = [CareerHypothesis(career_name="AI Research", confidence=0.3, status="discarded")]
    stage, _ = derive_understanding_level(
        career_dna=CareerDNA(), hypotheses=hypotheses, mode="exploration", has_hidden_potential=False
    )
    assert stage == "Seed"


def test_decision_ready_when_mode_is_recommendation():
    stage, _ = derive_understanding_level(
        career_dna=CareerDNA(), hypotheses=[], mode="recommendation", has_hidden_potential=False
    )
    assert stage == "Decision Ready"
