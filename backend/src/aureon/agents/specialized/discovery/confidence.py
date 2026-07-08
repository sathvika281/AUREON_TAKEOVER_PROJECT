"""Deterministic backstop for confidence scoring.

Mirrors the pattern already used for the recommendation gate
(agents/confidence_gate.py): the LLM proposes a judgment, but a
code-level ceiling bounds how fast it can grow, so confidence cannot be
talked up after only a handful of exchanges — this is "no responsible
system recommends after a few questions" enforced as code, not prompt
discipline.
"""

#: Roughly this many pieces of accumulated evidence before confidence can
#: even reach 1.0. Deliberately conservative — career decisions are not
#: made from a short chat.
EVIDENCE_COUNT_FOR_FULL_CONFIDENCE = 8


def deterministic_ceiling(evidence_count: int) -> float:
    return min(1.0, evidence_count / EVIDENCE_COUNT_FOR_FULL_CONFIDENCE)


def effective_confidence(llm_suggested: float, evidence_count: int) -> float:
    suggested = max(0.0, min(1.0, llm_suggested))
    return min(suggested, deterministic_ceiling(evidence_count))
