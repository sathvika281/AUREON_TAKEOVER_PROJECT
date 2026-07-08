from typing import Literal

#: A candidate with zero supporting evidence is capped near-zero
#: regardless of what the LLM claims — mirrors the hypothesis lifecycle's
#: deterministic-ceiling philosophy: status/strength is never
#: LLM-self-reported, always computed from the real evidence count.
NO_SUPPORT_CEILING = 0.2
SUPPORT_CEILING_BASE = 0.2
SUPPORT_CEILING_STEP = 0.15
CONTRADICTION_PENALTY = 0.1
MIN_CONFIDENCE = 0.05

#: Same thresholds as hypothesis_lifecycle.py's Investigating/Growing/Strong
#: boundaries, reused here so the two features read consistently.
STRONG_THRESHOLD = 0.6
GROWING_THRESHOLD = 0.3

EvidenceStrength = Literal["Strong", "Growing", "Needs More Evidence"]


def compute_candidate_confidence(
    llm_confidence: float, supporting_count: int, contradicting_count: int
) -> float:
    """Deterministic ceiling on the LLM's own stated confidence, driven by
    real evidence counts rather than trusting the number outright."""
    if supporting_count == 0:
        ceiling = NO_SUPPORT_CEILING
    else:
        ceiling = min(1.0, SUPPORT_CEILING_BASE + SUPPORT_CEILING_STEP * supporting_count)
    capped = min(llm_confidence, ceiling)
    penalized = capped - CONTRADICTION_PENALTY * contradicting_count
    return round(max(MIN_CONFIDENCE, penalized), 2)


def evidence_strength_label(confidence: float) -> EvidenceStrength:
    """The only confidence-derived value ever shown to the student — no
    raw number, same qualitative treatment as hypotheses' status labels."""
    if confidence >= STRONG_THRESHOLD:
        return "Strong"
    if confidence >= GROWING_THRESHOLD:
        return "Growing"
    return "Needs More Evidence"
