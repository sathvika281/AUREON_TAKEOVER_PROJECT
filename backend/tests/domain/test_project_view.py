from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.company import Company
from aureon.domain.models.project import Project
from aureon.domain.models.skill import Skill
from aureon.domain.services.project_view import build_project_detail_view, build_project_dto

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


def _project(**overrides) -> Project:
    defaults: dict = dict(
        id="genomics_dataset_explorer", title="Genomics Dataset Explorer",
        brief="Explore a real genomics dataset.", difficulty_level="intermediate", estimated_hours=8,
    )
    defaults.update(overrides)
    return Project(**defaults)


def _skill(**overrides) -> Skill:
    defaults: dict = dict(id="programming", name="Programming", category="technical", description="x")
    defaults.update(overrides)
    return Skill(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
    )
    defaults.update(overrides)
    return Career(**defaults)


def _company(**overrides) -> Company:
    defaults: dict = dict(id="illumina", name="Illumina", organization_kind="company", industry="biotechnology", what_they_do="x")
    defaults.update(overrides)
    return Company(**defaults)


def test_build_project_dto_maps_all_fields():
    project = _project(
        target_skill_ids=["programming", "statistical_analysis"],
        related_career_ids=["genomics_data_scientist"],
        related_company_ids=["illumina"],
        submission_type="github_repo",
    )
    dto = build_project_dto(project)
    assert dto.id == "genomics_dataset_explorer"
    assert dto.difficulty_level == "intermediate"
    assert dto.estimated_hours == 8
    assert dto.target_skill_ids == ["programming", "statistical_analysis"]
    assert dto.related_career_ids == ["genomics_data_scientist"]
    assert dto.related_company_ids == ["illumina"]
    assert dto.submission_type == "github_repo"


def test_project_detail_view_composes_real_resolved_entities():
    view = build_project_detail_view(
        _project(), target_skills=[_skill()], related_careers=[_career()], related_companies=[_company()],
    )
    assert view.project.id == "genomics_dataset_explorer"
    assert len(view.target_skills) == 1
    assert view.target_skills[0].id == "programming"
    assert len(view.related_careers) == 1
    assert view.related_careers[0].id == "genomics_data_scientist"
    assert len(view.related_companies) == 1
    assert view.related_companies[0].id == "illumina"


def test_project_detail_view_never_fabricates_unresolved_entities():
    # Nothing resolved in -> honestly empty, never guessed.
    view = build_project_detail_view(
        _project(), target_skills=[], related_careers=[], related_companies=[],
    )
    assert view.target_skills == []
    assert view.related_careers == []
    assert view.related_companies == []
