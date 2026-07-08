from aureon.agents.specialized.career_intelligence.confidence import (
    compute_candidate_confidence,
    evidence_strength_label,
)


def test_zero_supporting_evidence_caps_confidence_near_zero_regardless_of_llm_claim():
    result = compute_candidate_confidence(llm_confidence=0.95, supporting_count=0, contradicting_count=0)
    assert result <= 0.2


def test_more_supporting_evidence_raises_the_ceiling():
    low = compute_candidate_confidence(llm_confidence=0.9, supporting_count=1, contradicting_count=0)
    high = compute_candidate_confidence(llm_confidence=0.9, supporting_count=4, contradicting_count=0)
    assert high > low


def test_contradicting_evidence_lowers_confidence():
    without_contradiction = compute_candidate_confidence(
        llm_confidence=0.8, supporting_count=3, contradicting_count=0
    )
    with_contradiction = compute_candidate_confidence(
        llm_confidence=0.8, supporting_count=3, contradicting_count=2
    )
    assert with_contradiction < without_contradiction


def test_confidence_never_exceeds_llm_stated_value():
    result = compute_candidate_confidence(llm_confidence=0.1, supporting_count=10, contradicting_count=0)
    assert result <= 0.1


def test_evidence_strength_label_thresholds():
    assert evidence_strength_label(0.9) == "Strong"
    assert evidence_strength_label(0.6) == "Strong"
    assert evidence_strength_label(0.45) == "Growing"
    assert evidence_strength_label(0.3) == "Growing"
    assert evidence_strength_label(0.1) == "Needs More Evidence"
