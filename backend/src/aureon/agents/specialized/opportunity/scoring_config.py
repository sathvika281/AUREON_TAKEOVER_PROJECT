"""Responsibility: the single centralized home for every tunable number
and category-level template sentence used by Opportunity Fit scoring.
Owns: `FACTOR_WEIGHTS` and every other constant below. Does NOT own:
the scoring algorithm itself (scoring.py imports these, never
redefines a number inline) or per-factor computation logic. Consumed
by: `scoring.py`, `cost.py`.

Why centralized: re-weighting Career Alignment, adjusting the
readiness threshold, or tuning the smoothing behavior later is a
one-line change here — the algorithm code in scoring.py never changes.
Avoids scattering numeric weights throughout the codebase.
"""

from aureon.domain.models.opportunity import OpportunityCategory
from aureon.domain.models.opportunity_fit import FitFactorKey

FACTOR_WEIGHTS: dict[FitFactorKey, float] = {
    "career_alignment": 0.15,
    "skill_match": 0.20,
    "project_match": 0.15,
    "portfolio_strength": 0.10,
    "academic_eligibility": 0.10,
    "location": 0.05,
    "deadline": 0.05,
    "competition_level": 0.05,
    "evidence_quality": 0.10,
    "career_goal_alignment": 0.05,
}
# Enforced at import time, not just by convention.
assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9

READY_THRESHOLD = 0.65
NOT_READY_THRESHOLD = 0.40

SMOOTHING_MINOR_DELTA_THRESHOLD = 0.15
SMOOTHING_PREVIOUS_WEIGHT = 0.7
SMOOTHING_NEW_WEIGHT = 0.3

DATA_AVAILABLE_BASE = 0.3
DATA_AVAILABLE_STEP = 0.07

#: The factors a student can genuinely improve through effort — used for
#: Highest Impact Gap. deadline/location/competition_level/
#: academic_eligibility are excluded: a student can't "improve" their
#: way past a fixed deadline or admission level quickly.
IMPROVABLE_FACTORS: frozenset[FitFactorKey] = frozenset({
    "skill_match", "project_match", "portfolio_strength",
    "evidence_quality", "career_alignment", "career_goal_alignment",
})

#: Decimal places — overall_scores this close count as "similar fit"
#: for the long-term-trajectory tie-break in ranking.
RANKING_TIE_ROUNDING = 2

#: One honest, hedged sentence per category — never a specific claim
#: about one posting's real historical cadence, which Aureon doesn't have.
CATEGORY_CYCLE_NOTES: dict[OpportunityCategory, str] = {
    "internship": "similar internship cycles typically reopen annually",
    "hackathon": "similar hackathons are typically hosted a few times a year",
    "research_program": "similar research programs typically run on an annual cycle",
    "competition": "similar competitions are often annual",
    "scholarship": "similar scholarship cycles typically reopen annually",
    "open_source_program": "many open-source program cohorts run a few times a year",
    "fellowship": "fellowship cohorts typically run annually",
    "campus_ambassador_program": "ambassador cohorts are typically recruited once or twice a year",
    "conference": "this conference's next edition is typically about a year away",
    "workshop": "similar workshops are hosted periodically through the year",
    "bootcamp": "similar bootcamps often run multiple cohorts a year",
    "innovation_challenge": "similar challenges are typically hosted annually",
    # Explore Polish Batch — additive categories.
    "government_scheme": "government schemes often reopen on an annual or academic-year cycle",
    "mentorship_program": "mentorship cohorts are typically recruited a few times a year",
    "certification": "self-paced certifications are usually available to start at any time",
    "funding_grant": "similar funding rounds typically reopen annually",
    "community_program": "community programs typically accept new members on a rolling basis",
}

#: One honest, hedged sentence per category describing the primary
#: commitment preparing typically requires — `{duration}` is filled in
#: with the opportunity's own real duration_label.
CATEGORY_COMMITMENT_NOTES: dict[OpportunityCategory, str] = {
    "internship": "A sustained time commitment ({duration}) once accepted, plus focused skill prep beforehand.",
    "hackathon": "A short, intense time commitment ({duration}) plus focused skill prep beforehand.",
    "research_program": "A sustained commitment ({duration}), typically requiring deeper preparation.",
    "competition": "A build/preparation commitment ({duration}) ahead of a fixed deadline.",
    "scholarship": "Primarily an application-effort commitment (essays/documentation) rather than an ongoing time commitment.",
    "open_source_program": "A flexible, self-paced commitment ({duration}) that scales with your own availability.",
    "fellowship": "A significant, sustained commitment ({duration}) once accepted.",
    "campus_ambassador_program": "An ongoing, part-time commitment ({duration}) alongside your studies.",
    "conference": "A short attendance commitment ({duration}), light preparation.",
    "workshop": "A short attendance commitment ({duration}), minimal preparation.",
    "bootcamp": "An intensive, sustained time commitment ({duration}).",
    "innovation_challenge": "A build/preparation commitment ({duration}) ahead of a fixed deadline.",
    # Explore Polish Batch — additive categories.
    "government_scheme": "Primarily an application/documentation commitment rather than an ongoing time commitment.",
    "mentorship_program": "An ongoing, part-time commitment ({duration}) meeting regularly with a mentor.",
    "certification": "A self-paced study commitment ({duration}) you control the pace of.",
    "funding_grant": "Primarily an application-effort commitment (proposal/documentation) rather than an ongoing time commitment.",
    "community_program": "A flexible, self-paced commitment ({duration}) that scales with your own availability.",
}
