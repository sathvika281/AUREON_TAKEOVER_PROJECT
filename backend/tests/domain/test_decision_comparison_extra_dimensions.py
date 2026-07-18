from aureon.domain.services.decision_comparison_extra_dimensions import (
    EXTRA_COMPARISON_DIMENSIONS,
    build_extra_comparison_dimensions,
)
from aureon.domain.services.decision_workspace_service import (
    CardRecommendation,
    CareerDecisionCard,
    DecisionExplanation,
    ReadinessCheckpoints,
    RealityCheck,
)

from ._explore_factories import make_career


def _minimal_card(**overrides) -> CareerDecisionCard:
    defaults: dict = dict(
        career_id="c1", career_name="Test Career", one_liner="x", why_it_matters="x",
        confidence_label="Strong", confidence_band="High Confidence", demand_2030="x", demand_2035="x", demand_2040="x",
        readiness=ReadinessCheckpoints(False, False, False, False, False, False, False),
        reality_check=RealityCheck(daily_work="x", work_life_balance="x", stress="x", automation_risk="x", remote_possibility="x", travel="x", industry_outlook="x"),
        reasons_for=[], reasons_against=[], missing_evidence=[], explanation=DecisionExplanation(),
        hidden_strengths=[], relevant_interests=[], learning_style_pattern=None,
        unexplored_worlds=[], related_life_missions=[], top_journey_stories=[], top_knowledge_circles=[],
        top_opportunities=[], top_experts=[], decision_gaps=[], next_actions=[],
        recommendation=CardRecommendation(verdict="hold_for_now", reason="x"),
    )
    defaults.update(overrides)
    return CareerDecisionCard(**defaults)


def test_builds_all_six_dimensions_with_correct_ids():
    career = make_career(id="c1", name="Test Career", trait_tags=["leadership"])
    card = _minimal_card()
    dims = build_extra_comparison_dimensions([career], {"c1": card})
    assert [d.dimension for d in dims] == EXTRA_COMPARISON_DIMENSIONS
    for d in dims:
        assert "c1" in d.per_career


def test_leadership_emphasis_reflects_trait_tags():
    with_leadership = make_career(id="c1", trait_tags=["leadership"])
    without_leadership = make_career(id="c2", trait_tags=["curiosity"])
    card1 = _minimal_card(career_id="c1")
    card2 = _minimal_card(career_id="c2")
    dims = build_extra_comparison_dimensions([with_leadership, without_leadership], {"c1": card1, "c2": card2})
    leadership_dim = next(d for d in dims if d.dimension == "leadership_emphasis")
    assert "Yes" in leadership_dim.per_career["c1"]
    assert "Not typically" in leadership_dim.per_career["c2"]


def test_career_dna_alignment_reuses_confidence_band_verbatim():
    career = make_career(id="c1")
    card = _minimal_card(career_id="c1", confidence_band="Medium Confidence")
    dims = build_extra_comparison_dimensions([career], {"c1": card})
    dna_dim = next(d for d in dims if d.dimension == "career_dna_alignment")
    assert dna_dim.per_career["c1"] == "Medium Confidence"


def test_skips_careers_with_no_card():
    career = make_career(id="c1")
    dims = build_extra_comparison_dimensions([career], {})
    for d in dims:
        assert d.per_career == {}
