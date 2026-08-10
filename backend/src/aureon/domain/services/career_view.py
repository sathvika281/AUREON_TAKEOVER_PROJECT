from aureon.domain.models.career import Career, CareerStory
from aureon.domain.models.company import Company
from aureon.domain.models.project import Project
from aureon.domain.models.skill import Skill
from aureon.domain.models.trend import Trend
from aureon.domain.services.company_view import build_company_dto
from aureon.domain.services.project_view import build_project_dto
from aureon.domain.services.skill_view import build_skill_dto
from aureon.shared.schemas import (
    CareerBranchDTO,
    CareerDetailDTO,
    CareerFAQDTO,
    CareerRealityDTO,
    CareerStoryDTO,
    CareerSummaryDTO,
    FutureLensDTO,
    SalaryRangeDTO,
    TrendSummaryDTO,
)

"""Presentation mapping from the Career Knowledge Base -> API DTOs. Kept
separate from ``profile_view.py`` since it concerns the Career Knowledge
Base (careers/stories), not a student's own profile."""


def build_career_summary_dto(career: Career) -> CareerSummaryDTO:
    return CareerSummaryDTO(
        id=career.id,
        name=career.name,
        category=career.category,
        industry=career.industry,
        countries=career.countries,
        one_liner=career.one_liner,
        trait_tags=career.trait_tags,
    )


def _story_is_relevant(story: CareerStory, student_trait_tags: set[str] | None) -> bool:
    if not student_trait_tags:
        return False
    return bool(set(story.trait_tags) & student_trait_tags)


def build_career_detail_dto(
    career: Career,
    stories: list[CareerStory],
    *,
    student_trait_tags: set[str] | None = None,
    related_careers: list[Career] | None = None,
    recommended_next_exploration: Career | None = None,
    related_trends: list[Trend] | None = None,
    required_skills: list[Skill] | None = None,
    hiring_companies: list[Company] | None = None,
    related_projects: list[Project] | None = None,
) -> CareerDetailDTO:
    story_dtos = [
        CareerStoryDTO(
            id=s.id,
            career_id=s.career_id,
            person_label=s.person_label,
            background=s.background,
            journey=s.journey,
            challenges=s.challenges,
            turning_points=s.turning_points,
            advice=s.advice,
            lessons_learned=s.lessons_learned,
            relevant_to_student=_story_is_relevant(s, student_trait_tags),
        )
        for s in stories
    ]
    # Relevant stories first when we have a student to personalize for;
    # otherwise keep the natural (unsorted) order.
    if student_trait_tags:
        story_dtos.sort(key=lambda s: s.relevant_to_student, reverse=True)

    return CareerDetailDTO(
        id=career.id,
        name=career.name,
        category=career.category,
        industry=career.industry,
        countries=career.countries,
        one_liner=career.one_liner,
        trait_tags=career.trait_tags,
        reality=CareerRealityDTO(
            daily_work=career.reality.daily_work,
            work_environment=career.reality.work_environment,
            collaboration_level=career.reality.collaboration_level,
            creativity_level=career.reality.creativity_level,
            research_intensity=career.reality.research_intensity,
            learning_curve=career.reality.learning_curve,
            travel=career.reality.travel,
            remote_possibility=career.reality.remote_possibility,
            stress_factors=career.reality.stress_factors,
            typical_challenges=career.reality.typical_challenges,
            misconceptions=career.reality.misconceptions,
            long_term_growth=career.reality.long_term_growth,
            salary_ranges=[
                SalaryRangeDTO(region=r.region, range=r.range, note=r.note)
                for r in career.reality.salary_ranges
            ],
            required_education=career.reality.required_education,
            required_skills=career.reality.required_skills,
            entrepreneurship_potential=career.reality.entrepreneurship_potential,
        ),
        future_lens=FutureLensDTO(
            ai_impact=career.future_lens.ai_impact,
            automation_risk=career.future_lens.automation_risk,
            demand_2030=career.future_lens.demand_2030,
            demand_2035=career.future_lens.demand_2035,
            demand_2040=career.future_lens.demand_2040,
            emerging_opportunities=career.future_lens.emerging_opportunities,
            skills_becoming_valuable=career.future_lens.skills_becoming_valuable,
            timeline_narrative=career.future_lens.timeline_narrative,
        ),
        stories=story_dtos,
        description=career.description,
        why_people_love_it=career.why_people_love_it,
        branches=[CareerBranchDTO(name=b.name, description=b.description) for b in career.branches],
        related_careers=[build_career_summary_dto(c) for c in (related_careers or [])],
        recommended_next_exploration=(
            build_career_summary_dto(recommended_next_exploration) if recommended_next_exploration else None
        ),
        related_trends=[
            TrendSummaryDTO(id=t.id, title=t.title, category=t.category, summary=t.summary)
            for t in (related_trends or [])
        ],
        day_in_the_life=career.day_in_the_life,
        weekly_routine=career.weekly_routine,
        daily_tools=career.daily_tools,
        career_progression=career.career_progression,
        related_industries=career.related_industries,
        research_areas=career.research_areas,
        companies=career.companies,
        universities=career.universities,
        scholarships=career.scholarships,
        competitions=career.competitions,
        books=career.books,
        communities=career.communities,
        open_source_projects=career.open_source_projects,
        certifications=career.certifications,
        projects=career.projects,
        videos=career.videos,
        common_misconceptions=career.common_misconceptions,
        faqs=[CareerFAQDTO(question=f.question, answer=f.answer) for f in career.faqs],
        adjacent_careers=career.adjacent_careers,
        required_skills=[build_skill_dto(s) for s in (required_skills or [])],
        hiring_companies=[build_company_dto(co) for co in (hiring_companies or [])],
        related_projects=[build_project_dto(p) for p in (related_projects or [])],
    )
