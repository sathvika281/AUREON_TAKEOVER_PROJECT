from aureon.domain.models.career import Career, CareerStory
from aureon.shared.schemas import (
    CareerDetailDTO,
    CareerRealityDTO,
    CareerStoryDTO,
    CareerSummaryDTO,
    FutureLensDTO,
    SalaryRangeDTO,
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
    )
