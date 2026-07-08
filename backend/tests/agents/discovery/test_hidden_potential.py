from aureon.agents.specialized.discovery.hidden_potential import derive_hidden_potential
from aureon.domain.models.career_dna import CareerDNA, TraitSignal
from aureon.domain.models.evidence import EvidenceRecord


def test_no_pattern_below_two_strong_traits():
    dna = CareerDNA(traits={"curiosity": TraitSignal(score=0.8, summary="curious")})
    assert derive_hidden_potential(dna, []) == []


def test_pattern_found_and_cites_real_evidence():
    dna = CareerDNA(
        traits={
            "curiosity": TraitSignal(score=0.6, summary="curious"),
            "creativity": TraitSignal(score=0.7, summary="creative"),
        }
    )
    evidence = [
        EvidenceRecord(
            id="1", text="loves open-ended problems", source="conversation",
            related_trait="curiosity", relation="supports",
        ),
        EvidenceRecord(
            id="2", text="enjoys designing things", source="conversation",
            related_trait="creativity", relation="supports",
        ),
    ]
    patterns = derive_hidden_potential(dna, evidence)
    assert len(patterns) == 1
    assert "Curiosity" in patterns[0].sentence and "Creativity" in patterns[0].sentence
    assert "loves open-ended problems" in patterns[0].supporting_evidence
    assert "enjoys designing things" in patterns[0].supporting_evidence


def test_weak_trait_does_not_count():
    dna = CareerDNA(
        traits={
            "curiosity": TraitSignal(score=0.6, summary="curious"),
            "creativity": TraitSignal(score=0.2, summary="a little creative"),
        }
    )
    assert derive_hidden_potential(dna, []) == []
