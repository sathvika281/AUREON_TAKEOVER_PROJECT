from aureon.domain.models.career import Career, CareerReality, CareerStory, FutureLens
from aureon.domain.models.company import Company
from aureon.domain.models.project import Project
from aureon.domain.models.skill import Skill
from aureon.domain.services.career_view import build_career_detail_dto, build_career_summary_dto

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


def _career() -> Career:
    return Career(
        id="physician_general", name="Physician", category="traditional", industry="healthcare",
        one_liner="x", trait_tags=["communication", "values"], reality=_REALITY, future_lens=_FUTURE,
    )


def test_career_summary_dto_maps_core_fields():
    dto = build_career_summary_dto(_career())
    assert dto.id == "physician_general"
    assert dto.name == "Physician"


def test_stories_are_marked_relevant_when_trait_tags_overlap_student_traits():
    matching_story = CareerStory(
        id="s1", career_id="physician_general", person_label="Doctor, 5 years",
        background="x", journey="x", challenges="x", turning_points="x", advice="x",
        lessons_learned="x", trait_tags=["communication"],
    )
    non_matching_story = CareerStory(
        id="s2", career_id="physician_general", person_label="Doctor, 3 years",
        background="x", journey="x", challenges="x", turning_points="x", advice="x",
        lessons_learned="x", trait_tags=["leadership"],
    )

    dto = build_career_detail_dto(
        _career(), [non_matching_story, matching_story], student_trait_tags={"communication"}
    )

    assert dto.stories[0].id == "s1"
    assert dto.stories[0].relevant_to_student is True
    assert dto.stories[1].relevant_to_student is False


def test_stories_are_not_marked_relevant_without_a_student():
    story = CareerStory(
        id="s1", career_id="physician_general", person_label="Doctor, 5 years",
        background="x", journey="x", challenges="x", turning_points="x", advice="x",
        lessons_learned="x", trait_tags=["communication"],
    )

    dto = build_career_detail_dto(_career(), [story], student_trait_tags=None)

    assert dto.stories[0].relevant_to_student is False


def test_required_skills_default_to_empty_when_none_resolved():
    # A career whose required_skill_ids haven't been backfilled yet (or a
    # test that doesn't pass any) must never show a fabricated skill list.
    dto = build_career_detail_dto(_career(), [])
    assert dto.required_skills == []


def test_required_skills_are_resolved_into_real_dtos():
    skill = Skill(id="programming", name="Programming", category="technical", description="x")
    dto = build_career_detail_dto(_career(), [], required_skills=[skill])
    assert len(dto.required_skills) == 1
    assert dto.required_skills[0].id == "programming"
    assert dto.required_skills[0].name == "Programming"


def test_hiring_companies_default_to_empty_when_none_resolved():
    # A career whose company_ids haven't been backfilled yet must never
    # show a fabricated company list.
    dto = build_career_detail_dto(_career(), [])
    assert dto.hiring_companies == []


def test_hiring_companies_are_resolved_into_real_dtos():
    company = Company(id="google", name="Google", organization_kind="company", industry="technology", what_they_do="x")
    dto = build_career_detail_dto(_career(), [], hiring_companies=[company])
    assert len(dto.hiring_companies) == 1
    assert dto.hiring_companies[0].id == "google"
    assert dto.hiring_companies[0].name == "Google"


def test_related_projects_default_to_empty_when_none_resolved():
    # A career no project points back at yet must never show a
    # fabricated project list.
    dto = build_career_detail_dto(_career(), [])
    assert dto.related_projects == []


def test_related_projects_are_resolved_into_real_dtos():
    project = Project(
        id="genomics_dataset_explorer", title="Genomics Dataset Explorer", brief="x",
        difficulty_level="intermediate", estimated_hours=8,
    )
    dto = build_career_detail_dto(_career(), [], related_projects=[project])
    assert len(dto.related_projects) == 1
    assert dto.related_projects[0].id == "genomics_dataset_explorer"
    assert dto.related_projects[0].title == "Genomics Dataset Explorer"
