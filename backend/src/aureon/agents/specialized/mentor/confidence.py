"""Mentor Agent reuses Career Intelligence's confidence-capping directly —
the logic is generic (plain floats and counts, nothing career-specific),
so it's imported here rather than copied. Mirrors the same re-export
pattern used by decision/confidence.py before this relocation."""

from aureon.agents.specialized.career_intelligence.confidence import (
    compute_candidate_confidence,
    evidence_strength_label,
)

__all__ = ["compute_candidate_confidence", "evidence_strength_label"]
