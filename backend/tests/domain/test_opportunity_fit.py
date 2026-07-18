from aureon.domain.models.opportunity_fit import (
    FitFactor,
    HighestImpactGap,
    OpportunityCost,
    OpportunityFitResult,
    PreparationInsight,
)


def _factor(**overrides) -> FitFactor:
    defaults: dict = dict(
        key="skill_match", label="Skill Match", score=0.5, weight=0.2,
        data_available=True, rationale="x", evidence=["fact"],
    )
    defaults.update(overrides)
    return FitFactor(**defaults)


def test_fit_factor_carries_non_empty_evidence():
    assert _factor().evidence == ["fact"]


def test_opportunity_fit_result_rank_defaults_to_none_for_standalone_evaluation():
    result = OpportunityFitResult(
        opportunity_id="opp_1", overall_score=0.5, confidence=0.5, confidence_basis={},
        readiness_label="almost_ready", factors=[_factor()], requirements_met=1, requirements_total=3,
    )
    assert result.rank is None
    assert result.ranking_rationale is None
    assert result.generated_at is not None


def test_highest_impact_gap_shape():
    gap = HighestImpactGap(
        factor_key="skill_match", label="Skill Match", potential_score_gain=0.1,
        recommended_action="Build a project demonstrating this skill.",
    )
    assert gap.potential_score_gain == 0.1


def test_opportunity_cost_has_no_scoring_fields():
    """Structural proof that Opportunity Cost cannot feed back into
    ranking — it simply has no overall_score/rank field to influence."""
    cost = OpportunityCost(
        primary_commitment="x", estimated_preparation_effort="y",
        competing_saved_opportunities=[], deprioritization_note="z",
    )
    assert not hasattr(cost, "overall_score")
    assert not hasattr(cost, "rank")


def test_preparation_insight_shape():
    insight = PreparationInsight(why_recommended="x", recommended_preparation="y")
    assert insight.why_recommended == "x"
    assert insight.recommended_preparation == "y"
