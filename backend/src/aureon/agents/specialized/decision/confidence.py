"""Decision Agent reuses Career Intelligence's confidence-capping and
Evidence Strength labeling directly — the logic is generic (plain floats
and counts, nothing career-specific), so it's imported here rather than
copied. Mentor/College Match confidence uses the exact same deterministic
ceiling as Career Candidates."""

from aureon.agents.specialized.career_intelligence.confidence import (
    compute_candidate_confidence,
    evidence_strength_label,
)

__all__ = ["compute_candidate_confidence", "evidence_strength_label"]
