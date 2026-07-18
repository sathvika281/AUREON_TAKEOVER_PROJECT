"""Shared, non-collected (no test_ prefix) fixture builders for Explore
Batch 1 tests."""

from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_world import CareerWorld


def make_career(**overrides) -> Career:
    defaults: dict = dict(
        id="career_1", name="Test Career", category="emerging", industry="technology",
        one_liner="A test career.", trait_tags=[],
        reality=CareerReality(
            daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
            research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
            stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
            required_education="x",
        ),
        future_lens=FutureLens(
            ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
            emerging_opportunities="x", timeline_narrative="x",
        ),
    )
    defaults.update(overrides)
    return Career(**defaults)


def make_career_world(**overrides) -> CareerWorld:
    defaults: dict = dict(
        id="world_1", name="Test World", description="x", why_it_matters="x",
        global_importance="x", future_growth="x", related_industries=["technology"],
    )
    defaults.update(overrides)
    return CareerWorld(**defaults)
