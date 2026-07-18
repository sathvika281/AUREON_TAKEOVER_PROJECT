"""Responsibility: Opportunity Equality's ranking — "these are
opportunities you are least likely to discover on your own," never
"here are today's opportunities." Owns: ``find_equality_opportunities``,
``OpportunityEqualityRecommendation``. Does NOT own: fit/eligibility
scoring (reuses ``agents/specialized/opportunity/scoring.py::score_opportunity``
unmodified — Opportunity Hub's own tested output is never edited) or
exposure-gap computation (``domain/services/exposure_gap.py``).
Consumed by: ``api/v1/opportunity_equality.py``.

Ranks by real exposure gap first (lowest likelihood of self-discovery),
among opportunities the student is genuinely eligible-adjacent for
(excludes ``readiness_label == "not_ready"`` — never surfaces something
wildly out of reach). Never mutates Opportunity Hub's own
``OpportunityFitResult``/ranking.
"""

from datetime import datetime

from pydantic import BaseModel

from aureon.agents.specialized.opportunity.scoring import score_opportunity
from aureon.domain.models.career_memory import CareerMemory
from aureon.domain.models.exposure_gap import ExposureGapInsight
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.exposure_gap import compute_exposure_gap
from aureon.domain.services.world_signal_alignment import compute_tag_alignment

_LIKELIHOOD_RANK = {"low": 0, "medium": 1, "high": 2}


class OpportunityEqualityRecommendation(BaseModel):
    opportunity: Opportunity
    fit: OpportunityFitResult
    exposure_gap: ExposureGapInsight


def find_equality_opportunities(
    profile: StudentProfile,
    memory: CareerMemory,
    opportunities: list[Opportunity],
    *,
    now: datetime,
    top_n: int = 5,
) -> list[OpportunityEqualityRecommendation]:
    world_signals = profile.discovery_onboarding.world_signals
    recommendations: list[OpportunityEqualityRecommendation] = []

    for opportunity in opportunities:
        if not opportunity.is_active:
            continue
        fit = score_opportunity(
            profile, memory, opportunity, now=now,
            previous_score=memory.opportunities.score_history.get(opportunity.id),
        )
        if fit.readiness_label == "not_ready":
            continue  # eligible-adjacent only — never wildly out of reach

        alignment = compute_tag_alignment([*opportunity.domain_tags, opportunity.category], world_signals)
        exposure_gap = compute_exposure_gap(opportunity, profile, memory, world_signal_alignment=alignment)
        recommendations.append(
            OpportunityEqualityRecommendation(opportunity=opportunity, fit=fit, exposure_gap=exposure_gap)
        )

    recommendations.sort(
        key=lambda r: (_LIKELIHOOD_RANK[r.exposure_gap.likelihood_of_self_discovery], -r.fit.overall_score)
    )
    return recommendations[:top_n]
