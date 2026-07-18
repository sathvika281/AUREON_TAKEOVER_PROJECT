"""Responsibility: Opportunity Cost — an informational trade-off aid,
never a scoring factor. Owns: `derive_opportunity_cost`. Does NOT own:
`overall_score`/`rank` (Opportunity Cost is computed after ranking is
finalized and never fed back into it — see agent.py's find_opportunities
call order). Consumed by: `OpportunityAgent.find_opportunities`, which
attaches the result to `OpportunityRecommendation.cost`.

No speculation, no invented success rates, no fabricated hour counts —
every sentence is either a category-level hedged norm (scoring_config.py's
CATEGORY_COMMITMENT_NOTES, same honest-hedging convention as
CATEGORY_CYCLE_NOTES) or a real cross-reference against the student's
own tracked opportunities (never a generic "you might need to skip your
hobbies" guess).
"""

from datetime import timedelta

from aureon.agents.specialized.opportunity.scoring_config import CATEGORY_COMMITMENT_NOTES
from aureon.domain.models.career_memory import OpportunityEntry
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import OpportunityCost, OpportunityFitResult

_COMPETING_WINDOW_DAYS = 14


def derive_opportunity_cost(
    opportunity: Opportunity,
    fit: OpportunityFitResult,
    other_tracked: list[tuple[OpportunityEntry, Opportunity]],
) -> OpportunityCost:
    primary_commitment = CATEGORY_COMMITMENT_NOTES[opportunity.category].format(duration=opportunity.duration_label)

    # Effort scales with real readiness (more gap = more prep work) and
    # real competitiveness (a highly competitive posting demands more
    # than bare eligibility) — never a fabricated hour estimate.
    if fit.readiness_label == "ready":
        effort = "Likely light preparation — you already meet most requirements."
    elif fit.readiness_label == "almost_ready":
        effort = "Likely a few weeks of focused preparation on your remaining gap areas."
    else:
        effort = "Likely a significant preparation investment — multiple gap areas need real work first."
    if opportunity.estimated_competitiveness in ("high", "very_high"):
        effort += " Given how competitive this is, meeting the bare minimum likely won't be enough."

    # Real evidence only: other opportunities THIS student has actually
    # saved/viewed whose deadlines fall in a similar window or share
    # this one's category. Category matching never requires this
    # opportunity to have a deadline of its own — only the deadline-
    # window check does.
    window_start = window_end = None
    if opportunity.application_deadline is not None:
        window_start = opportunity.application_deadline - timedelta(days=_COMPETING_WINDOW_DAYS)
        window_end = opportunity.application_deadline + timedelta(days=_COMPETING_WINDOW_DAYS)

    competing: list[str] = []
    for entry, other_opp in other_tracked:
        if entry.interaction not in ("viewed", "saved") or other_opp.id == opportunity.id:
            continue
        same_category = other_opp.category == opportunity.category
        overlapping_deadline = (
            window_start is not None
            and other_opp.application_deadline is not None
            and window_start <= other_opp.application_deadline <= window_end
        )
        if same_category or overlapping_deadline:
            competing.append(other_opp.title)

    if competing:
        note = (
            f"Preparing for this may compete for time with {len(competing)} other opportunity/opportunities "
            "you've already saved or viewed in a similar window or category."
        )
    else:
        note = (
            "No other saved or viewed opportunities currently overlap with this one's category or timing — "
            "the trade-off against your other specific plans can't be estimated beyond this."
        )

    return OpportunityCost(
        primary_commitment=primary_commitment,
        estimated_preparation_effort=effort,
        competing_saved_opportunities=competing,
        deprioritization_note=note,
    )
