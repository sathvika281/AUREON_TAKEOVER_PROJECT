"""Shared, non-collected (no test_ prefix) fixture builders for Decide
Batch 1 tests."""

from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.experiment import Experiment
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.learning_style import LearningStyle
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import FitFactor, OpportunityFitResult
from aureon.domain.models.exposure_gap import ExposureGapInsight
from aureon.domain.services.opportunity_equality import OpportunityEqualityRecommendation


def make_career_candidate(**overrides) -> CareerCandidate:
    defaults: dict = dict(
        id="candidate_1", career_id="c1", career_name="Test Career", why_it_matches="x", confidence=0.7,
    )
    defaults.update(overrides)
    return CareerCandidate(**defaults)


def make_life_mission(**overrides) -> LifeMission:
    defaults: dict = dict(id="mission_1", name="Solve Climate Problems", description="x")
    defaults.update(overrides)
    return LifeMission(**defaults)


def make_learning_style(**overrides) -> LearningStyle:
    defaults: dict = dict(id="style_1", name="Hands-On Experimenter", description="x")
    defaults.update(overrides)
    return LearningStyle(**defaults)


def make_experiment(**overrides) -> Experiment:
    defaults: dict = dict(
        id="experiment_1", title="Test Experiment", category="debug_code", description="x", instructions="x",
        estimated_minutes=30, age_appropriate_note="x", related_world="world_1", reflection_prompt="x",
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def make_opportunity(**overrides) -> Opportunity:
    defaults: dict = dict(
        id="opportunity_1", title="Test Opportunity", category="internship", organization="Test Org",
        organization_kind="company", description="x", location="Remote", duration_label="8 weeks",
        official_link="https://example.com",
    )
    defaults.update(overrides)
    return Opportunity(**defaults)


def make_opportunity_recommendation(**overrides) -> OpportunityEqualityRecommendation:
    opportunity = overrides.pop("opportunity", None) or make_opportunity()
    fit = overrides.pop("fit", None) or OpportunityFitResult(
        opportunity_id=opportunity.id, overall_score=0.5, confidence=0.5,
        confidence_basis={"factors_with_real_signal": 1, "factors_total": 10, "smoothed": False},
        readiness_label="almost_ready", factors=[], requirements_met=1, requirements_total=2,
    )
    exposure_gap = overrides.pop("exposure_gap", None) or ExposureGapInsight(
        likelihood_of_self_discovery="low", why_shown="x", contributing_factors=["x"],
    )
    return OpportunityEqualityRecommendation(opportunity=opportunity, fit=fit, exposure_gap=exposure_gap)
