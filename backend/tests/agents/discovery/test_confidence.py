from aureon.agents.specialized.discovery.confidence import (
    EVIDENCE_COUNT_FOR_FULL_CONFIDENCE,
    deterministic_ceiling,
    effective_confidence,
)


def test_ceiling_grows_linearly_with_evidence_count():
    assert deterministic_ceiling(0) == 0.0
    assert deterministic_ceiling(EVIDENCE_COUNT_FOR_FULL_CONFIDENCE) == 1.0
    assert deterministic_ceiling(EVIDENCE_COUNT_FOR_FULL_CONFIDENCE * 2) == 1.0


def test_ceiling_blocks_llm_from_overclaiming_confidence_early():
    # After only one piece of evidence, even a maximally confident LLM
    # judgment must be bounded far below 1.0.
    result = effective_confidence(llm_suggested=1.0, evidence_count=1)
    assert result == deterministic_ceiling(1)
    assert result < 0.3


def test_effective_confidence_never_exceeds_llm_suggestion_either():
    result = effective_confidence(llm_suggested=0.1, evidence_count=100)
    assert result == 0.1


def test_effective_confidence_clamps_out_of_range_llm_values():
    assert effective_confidence(llm_suggested=1.5, evidence_count=100) == 1.0
    assert effective_confidence(llm_suggested=-0.5, evidence_count=100) == 0.0
