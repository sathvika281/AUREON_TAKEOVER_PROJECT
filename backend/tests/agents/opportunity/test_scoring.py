from datetime import datetime, timedelta, timezone

import pytest

from aureon.agents.specialized.opportunity.scoring import (
    _highest_impact_gap,
    explain_ranking,
    score_opportunity,
)
from aureon.agents.specialized.opportunity.scoring_config import FACTOR_WEIGHTS
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.career_memory import (
    CareerMemory,
    EvidenceArtifact,
    EvidenceMemory,
    GrowthMemory,
    GrowthSkill,
    IdentityMemory,
)
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.opportunity_fit import FitFactor, HighestImpactGap
from aureon.domain.models.student_profile import StudentProfile
from tests.agents.opportunity._factories import make_opportunity

NOW = datetime.now(timezone.utc)


def _empty_profile() -> StudentProfile:
    return StudentProfile(student_id="s1")


def _rich_profile() -> StudentProfile:
    return StudentProfile(
        student_id="s1",
        goals=["AI research"],
        career_hypotheses=[CareerHypothesis(career_name="AI Researcher", confidence=0.7)],
        evidence_graph=[
            EvidenceRecord(id="e1", text="Built a machine learning pipeline", source="github", relation="supports")
        ],
    )


def _rich_memory() -> CareerMemory:
    return CareerMemory(
        identity=IdentityMemory(academic_level="undergraduate", location_country="Germany"),
        evidence=EvidenceMemory(
            artifacts=[EvidenceArtifact(kind="project", ref_id="p1", title="Machine learning pipeline")]
        ),
        growth=GrowthMemory(skills=[GrowthSkill(skill="python", status="mastered", evidence="Shipped 3 projects")]),
    )


def test_factor_weights_sum_to_one():
    assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9


@pytest.mark.parametrize("profile,memory", [(_empty_profile(), CareerMemory()), (_rich_profile(), _rich_memory())])
def test_every_factor_carries_non_empty_evidence(profile, memory):
    opportunity = make_opportunity(min_academic_level="undergraduate", countries=["Germany"], is_remote=False)
    result = score_opportunity(profile, memory, opportunity, now=NOW)
    assert len(result.factors) == 10
    for factor in result.factors:
        assert len(factor.evidence) > 0, f"{factor.key} has no evidence"


def test_requirements_tally_counts_real_matches():
    opportunity = make_opportunity(
        required_skills=["python", "machine learning"], min_academic_level="undergraduate", countries=["Germany"], is_remote=False
    )
    result = score_opportunity(_rich_profile(), _rich_memory(), opportunity, now=NOW)

    assert result.requirements_total == len(opportunity.required_skills) + 2
    # python (mastered) + machine learning (evidence text match) + academic + location
    assert result.requirements_met == 4


def test_fairness_missing_data_never_penalized_and_says_so():
    opportunity = make_opportunity(min_academic_level="undergraduate")
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)

    factor_by_key = {f.key: f for f in result.factors}
    assert factor_by_key["career_alignment"].data_available is False
    assert "does not count against you" in factor_by_key["career_alignment"].rationale
    assert factor_by_key["academic_eligibility"].data_available is False
    assert "does not count against you" in factor_by_key["academic_eligibility"].rationale


def test_smoothing_blends_a_minor_score_change():
    opportunity = make_opportunity()
    previous_score = 0.5
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW, previous_score=previous_score)

    raw = sum(f.score * f.weight for f in result.factors)
    if abs(raw - previous_score) <= 0.15:
        assert result.confidence_basis["smoothed"] is True
        assert result.overall_score == round(0.7 * previous_score + 0.3 * raw, 4)


def test_smoothing_uses_raw_score_for_a_significant_change():
    opportunity = make_opportunity(min_academic_level="undergraduate", countries=["Germany"], is_remote=False)
    previous_score = 0.0  # far below any realistic rich-profile score -> significant delta
    result = score_opportunity(_rich_profile(), _rich_memory(), opportunity, now=NOW, previous_score=previous_score)

    raw = sum(f.score * f.weight for f in result.factors)
    assert abs(raw - previous_score) > 0.15
    assert result.confidence_basis["smoothed"] is False
    assert result.overall_score == round(raw, 4)


@pytest.mark.parametrize(
    "days_left,expect_substring",
    [(5, "Only"), (20, "enough time"), (60, "real room")],
)
def test_timing_rationale_reflects_real_deadline_distance(days_left, expect_substring):
    opportunity = make_opportunity(application_deadline=NOW + timedelta(days=days_left))
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    assert expect_substring in result.timing_rationale


def test_timing_rationale_for_rolling_admissions():
    opportunity = make_opportunity(application_deadline=None)
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    assert "Rolling admissions" in result.timing_rationale


def test_consequence_if_ignored_for_urgent_deadline():
    opportunity = make_opportunity(application_deadline=NOW + timedelta(days=5))
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    assert "closes soon" in result.consequence_if_ignored


def test_consequence_if_ignored_names_the_real_highest_impact_gap_when_no_urgent_deadline():
    opportunity = make_opportunity(application_deadline=NOW + timedelta(days=90))
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    assert result.highest_impact_gap is not None
    assert result.highest_impact_gap.label in result.consequence_if_ignored


def test_highest_impact_gap_selects_largest_potential_gain():
    factors = [
        FitFactor(key="skill_match", label="Skill Match", score=0.2, weight=0.20, data_available=True, rationale="a", evidence=["e"]),
        FitFactor(key="project_match", label="Project Match", score=0.9, weight=0.15, data_available=True, rationale="b", evidence=["e"]),
        FitFactor(key="deadline", label="Deadline", score=0.1, weight=0.05, data_available=True, rationale="c", evidence=["e"]),
    ]
    gap = _highest_impact_gap(factors)
    assert isinstance(gap, HighestImpactGap)
    # skill_match: (1-0.2)*0.20=0.16 vs project_match: (1-0.9)*0.15=0.015 vs deadline excluded (not improvable)
    assert gap.factor_key == "skill_match"


def test_highest_impact_gap_is_none_when_every_improvable_factor_is_perfect():
    factors = [
        FitFactor(key=key, label=key, score=1.0, weight=weight, data_available=True, rationale="x", evidence=["e"])
        for key, weight in FACTOR_WEIGHTS.items()
    ]
    assert _highest_impact_gap(factors) is None


def test_explain_ranking_scoped_to_same_category_peers():
    strong = make_opportunity(id="opp_strong", category="internship")
    weak = make_opportunity(id="opp_weak", category="internship")
    fit_strong = score_opportunity(_rich_profile(), _rich_memory(), strong, now=NOW)
    fit_weak = score_opportunity(_empty_profile(), CareerMemory(), weak, now=NOW)
    fit_strong.opportunity_id, fit_weak.opportunity_id = "opp_strong", "opp_weak"

    title_by_id = {"opp_strong": "Strong Internship", "opp_weak": "Weak Internship"}
    message = explain_ranking(fit_strong, [fit_strong, fit_weak], title_by_id)
    assert "Weak Internship" in message


def test_explain_ranking_handles_sole_result_in_category():
    opportunity = make_opportunity()
    fit = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    message = explain_ranking(fit, [fit], {fit.opportunity_id: "Solo"})
    assert "only opportunity" in message.lower()


@pytest.mark.parametrize(
    "category",
    ["government_scheme", "mentorship_program", "certification", "funding_grant", "community_program"],
)
def test_timing_rationale_never_key_errors_for_new_categories(category):
    """Explore Polish Batch — CATEGORY_CYCLE_NOTES is indexed
    unconditionally by opportunity.category whenever a deadline is set;
    confirms the 5 newly-added categories were given real entries."""
    opportunity = make_opportunity(category=category, application_deadline=NOW + timedelta(days=20))
    result = score_opportunity(_empty_profile(), CareerMemory(), opportunity, now=NOW)
    assert result.timing_rationale
