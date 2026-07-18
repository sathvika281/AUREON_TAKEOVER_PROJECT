from datetime import datetime, timedelta, timezone

import pytest

from aureon.agents.specialized.opportunity.cost import derive_opportunity_cost
from aureon.domain.models.career_memory import OpportunityEntry
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from tests.agents.opportunity._factories import make_opportunity

NOW = datetime.now(timezone.utc)


def _fit(readiness_label="almost_ready") -> OpportunityFitResult:
    return OpportunityFitResult(
        opportunity_id="opp_1", overall_score=0.5, confidence=0.5, confidence_basis={},
        readiness_label=readiness_label, factors=[], requirements_met=2, requirements_total=5,
    )


def test_effort_scales_with_readiness_ready():
    opportunity = make_opportunity(estimated_competitiveness="low")
    cost = derive_opportunity_cost(opportunity, _fit("ready"), [])
    assert "light preparation" in cost.estimated_preparation_effort


def test_effort_scales_with_readiness_not_ready():
    opportunity = make_opportunity(estimated_competitiveness="low")
    cost = derive_opportunity_cost(opportunity, _fit("not_ready"), [])
    assert "significant preparation" in cost.estimated_preparation_effort


def test_effort_notes_high_competitiveness():
    opportunity = make_opportunity(estimated_competitiveness="very_high")
    cost = derive_opportunity_cost(opportunity, _fit("ready"), [])
    assert "competitive" in cost.estimated_preparation_effort


def test_no_competing_opportunities_gives_honest_cant_estimate_note():
    opportunity = make_opportunity(application_deadline=NOW + timedelta(days=10))
    cost = derive_opportunity_cost(opportunity, _fit(), [])
    assert cost.competing_saved_opportunities == []
    assert "can't be estimated" in cost.deprioritization_note


def test_names_a_real_competing_opportunity_by_matching_category():
    opportunity = make_opportunity(id="opp_1", category="internship", application_deadline=None)
    other = make_opportunity(id="opp_2", category="internship", title="Other Internship", application_deadline=None)
    entry = OpportunityEntry(interaction="saved", category="internship", ref_id="opp_2", opportunity_version=1, title="Other Internship", occurred_at=NOW)

    cost = derive_opportunity_cost(opportunity, _fit(), [(entry, other)])

    assert cost.competing_saved_opportunities == ["Other Internship"]
    assert "1 other opportunity" in cost.deprioritization_note


def test_names_a_real_competing_opportunity_by_overlapping_deadline_window():
    opportunity = make_opportunity(id="opp_1", category="internship", application_deadline=NOW + timedelta(days=30))
    other = make_opportunity(id="opp_2", category="hackathon", title="Overlapping Hackathon", application_deadline=NOW + timedelta(days=35))
    entry = OpportunityEntry(interaction="viewed", category="hackathon", ref_id="opp_2", opportunity_version=1, title="Overlapping Hackathon", occurred_at=NOW)

    cost = derive_opportunity_cost(opportunity, _fit(), [(entry, other)])

    assert cost.competing_saved_opportunities == ["Overlapping Hackathon"]


def test_applied_or_rejected_interactions_never_count_as_competing():
    opportunity = make_opportunity(id="opp_1", category="internship", application_deadline=None)
    other = make_opportunity(id="opp_2", category="internship", title="Already Applied", application_deadline=None)
    entry = OpportunityEntry(interaction="applied", category="internship", ref_id="opp_2", opportunity_version=1, title="Already Applied", occurred_at=NOW)

    cost = derive_opportunity_cost(opportunity, _fit(), [(entry, other)])

    assert cost.competing_saved_opportunities == []


def test_never_produces_a_score_or_rank_field():
    opportunity = make_opportunity()
    cost = derive_opportunity_cost(opportunity, _fit(), [])
    assert not hasattr(cost, "overall_score")
    assert not hasattr(cost, "rank")


@pytest.mark.parametrize(
    "category",
    ["government_scheme", "mentorship_program", "certification", "funding_grant", "community_program"],
)
def test_commitment_note_never_key_errors_for_new_categories(category):
    """Explore Polish Batch — CATEGORY_COMMITMENT_NOTES is indexed
    unconditionally by opportunity.category on every call; confirms the
    5 newly-added categories were given real entries."""
    opportunity = make_opportunity(category=category)
    cost = derive_opportunity_cost(opportunity, _fit(), [])
    assert cost.primary_commitment
