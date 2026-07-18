"""Responsibility: the deterministic output shapes of Opportunity Fit
scoring. Owns: `FitFactor`, `HighestImpactGap`, `OpportunityFitResult`,
`PreparationInsight`, `OpportunityCost`. Does NOT own: the scoring
algorithm itself (agents/specialized/opportunity/scoring.py) — these
are pure data shapes. Lives in `domain/models/` (not under
`agents/specialized/`) for the same reason `ProgressReport` does:
`services/foundation/journey_guidance.py` needs to import
`OpportunityFitResult` without creating a
`services/foundation -> agents/specialized` dependency.

Why deterministic scoring, stated once here since every consumer reads
this module: a student must be able to see exactly why a number is
what it is — no factor is ever a hidden black box, and every factor
carries real, non-empty evidence (see FitFactor.evidence).

Together, `PreparationInsight.why_recommended` + `OpportunityFitResult`'s
`ranking_rationale` + `highest_impact_gap` + `timing_rationale` +
`consequence_if_ignored` are the concrete, real answers to the five
questions a student actually asks: why this matters, why now, why
ranked here, what to improve, what happens if ignored — every one
grounded in already-computed facts, never a second free-form judgment.
"""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

FitFactorKey = Literal[
    "career_alignment",
    "skill_match",
    "project_match",
    "portfolio_strength",
    "academic_eligibility",
    "location",
    "deadline",
    "competition_level",
    "evidence_quality",
    "career_goal_alignment",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FitFactor(BaseModel):
    """One scoring dimension, always individually inspectable — never
    just a number. `evidence` must never be empty (see scoring.py's
    module docstring for the enforced contract): even a thin factor
    like `deadline` states the concrete real fact behind its score."""

    key: FitFactorKey
    label: str
    score: float  # 0.0-1.0, always deterministic, never LLM-asserted
    weight: float
    #: False = the profile has no real signal for this factor yet —
    #: scored neutral, never penalized (see Fairness in scoring.py).
    data_available: bool
    rationale: str
    evidence: list[str] = Field(default_factory=list)


class HighestImpactGap(BaseModel):
    """The single improvement that would most increase this student's
    readiness — not every missing requirement at once."""

    factor_key: FitFactorKey
    label: str
    potential_score_gain: float
    recommended_action: str


class OpportunityFitResult(BaseModel):
    """Opportunity Fit's one structured artifact — always all 10
    factors, never hidden reasoning."""

    opportunity_id: str
    overall_score: float
    confidence: float
    #: {"factors_with_real_signal": int, "factors_total": int, "smoothed": bool}
    confidence_basis: dict[str, Any]
    readiness_label: Literal["ready", "almost_ready", "not_ready"]
    factors: list[FitFactor]
    highest_impact_gap: HighestImpactGap | None = None
    #: Why now instead of later — deterministic, grounded in the real
    #: deadline + an honestly-hedged category norm.
    timing_rationale: str = ""
    #: What will likely happen if this is skipped — deterministic,
    #: grounded in the real deadline/highest_impact_gap.
    consequence_if_ignored: str = ""
    requirements_met: int
    requirements_total: int
    met_requirement_labels: list[str] = Field(default_factory=list)
    unmet_requirement_labels: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    #: Set by find_opportunities once a batch is sorted; None for a
    #: standalone evaluate_fit call with no batch context.
    rank: int | None = None
    ranking_rationale: str | None = None
    generated_at: datetime = Field(default_factory=_utcnow)


class PreparationInsight(BaseModel):
    """The one narrative layer on top of OpportunityFitResult's
    deterministic facts — same facts-vs-narrative split as
    ProgressReport/ProgressDimension. The LLM that produces this never
    sees raw profile data, only these already-computed facts, so it
    cannot invent a requirement/skill/deadline/evidence item."""

    why_recommended: str
    recommended_preparation: str


class OpportunityCost(BaseModel):
    """Informational only — never a scoring factor, never influences
    `overall_score`/`rank`. Answers: what commitment does preparing
    require, what else might reasonably compete for the student's time,
    roughly how much preparation effort is likely. Every field is
    deterministic, grounded only in opportunity.category/
    estimated_competitiveness/required_skills/duration_label/
    application_deadline and the student's own real tracked
    opportunities — never a speculative or invented trade-off."""

    primary_commitment: str
    estimated_preparation_effort: str
    #: Real titles of the student's own other saved/viewed opportunities
    #: that overlap in category or deadline window — empty (with an
    #: honest note) when none exist, never a generic guess.
    competing_saved_opportunities: list[str] = Field(default_factory=list)
    deprioritization_note: str
