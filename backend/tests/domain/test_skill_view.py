from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.skill import Skill
from aureon.domain.services.skill_view import build_skill_detail_view, build_skill_dto

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)


def _skill(**overrides) -> Skill:
    defaults: dict = dict(
        id="programming", name="Programming", category="technical",
        description="Writing and debugging code.",
    )
    defaults.update(overrides)
    return Skill(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
    )
    defaults.update(overrides)
    return Career(**defaults)


def test_build_skill_dto_maps_all_fields():
    skill = _skill(
        parent_skill_id="data_science", related_skill_ids=["statistical_analysis"],
        evidence_types_that_count=["a completed project"],
    )
    dto = build_skill_dto(skill)
    assert dto.id == "programming"
    assert dto.category == "technical"
    assert dto.parent_skill_id == "data_science"
    assert dto.related_skill_ids == ["statistical_analysis"]
    assert dto.evidence_types_that_count == ["a completed project"]


def test_skill_detail_view_composes_real_requiring_careers():
    skill = _skill()
    career = _career()
    view = build_skill_detail_view(skill, [career])
    assert view.skill.id == "programming"
    assert len(view.careers_requiring_it) == 1
    assert view.careers_requiring_it[0].id == "genomics_data_scientist"


def test_skill_detail_view_never_fabricates_requiring_careers():
    # No requiring careers passed in -> honestly empty, never guessed.
    view = build_skill_detail_view(_skill(), [])
    assert view.careers_requiring_it == []
