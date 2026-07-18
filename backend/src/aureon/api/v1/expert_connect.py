from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_event_repository,
    get_career_repository,
    get_expert_repository,
    get_mentorship_repository,
)
from aureon.domain.services.career_experience_view import generate_available_slots
from aureon.domain.services.expert_journey_service import build_expert_journey
from aureon.domain.services.expert_knowledge_service import build_expert_knowledge
from aureon.domain.services.expert_profile_service import build_expert_profile
from aureon.domain.services.mentorship_service import count_active_mentees
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.mentorship_repository import MentorshipRepository
from aureon.shared.schemas import (
    CareerEventDTO,
    CareerFAQDTO,
    CareerJourneyMilestoneDTO,
    ExpertDetailDTO,
    ExpertFiltersResponse,
    ExpertSearchResponse,
    ExpertSummaryDTO,
    LinkRefDTO,
)

router = APIRouter(prefix="/experts", tags=["expert-connect"])


def _summary_dto(expert) -> ExpertSummaryDTO:
    return ExpertSummaryDTO(
        id=expert.id, name=expert.name, profession=expert.profession,
        specialization=expert.specialization, country=expert.country, city=expert.city,
        years_experience=expert.years_experience, industries=expert.industries,
        organization=expert.organization, trait_tags=expert.trait_tags,
        who_should_talk_to_me=expert.who_should_talk_to_me, photo_url=expert.photo_url,
        updated_at=expert.updated_at,
    )


@router.get("", response_model=ExpertSearchResponse)
async def search_experts(
    q: str | None = None,
    specialization: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    min_years_experience: int | None = None,
    accepts_mentorship: bool | None = None,
    limit: int = 100,
    offset: int = 0,
    experts: ExpertRepository = Depends(get_expert_repository),
) -> ExpertSearchResponse:
    """Expert Connect's directory endpoint — always open, no gating.
    Every expert here is a real `Mentor` row (an expert IS a Mentor);
    see `domain/models/mentor.py`."""
    results, total = await experts.search_experts(
        q=q, specialization=specialization, industry=industry, country=country,
        min_years_experience=min_years_experience, accepts_mentorship=accepts_mentorship,
        limit=limit, offset=offset,
    )
    return ExpertSearchResponse(
        experts=[_summary_dto(e) for e in results], total=total, limit=limit, offset=offset,
    )


@router.get("/filters", response_model=ExpertFiltersResponse)
async def get_expert_filters(
    experts: ExpertRepository = Depends(get_expert_repository),
) -> ExpertFiltersResponse:
    specializations, industries, countries = await experts.list_filter_values()
    return ExpertFiltersResponse(specializations=specializations, industries=industries, countries=countries)


@router.get("/{expert_id}", response_model=ExpertDetailDTO)
async def get_expert_detail(
    expert_id: str,
    experts: ExpertRepository = Depends(get_expert_repository),
    careers: CareerRepository = Depends(get_career_repository),
    events: CareerEventRepository = Depends(get_career_event_repository),
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> ExpertDetailDTO:
    expert = await experts.get_expert(expert_id)
    if expert is None:
        raise HTTPException(status_code=404, detail="Expert not found")

    career_catalog = await careers.list_careers()
    expert_mentorships = await mentorships.list_for_expert(expert_id)
    current_mentee_count = count_active_mentees(expert_mentorships, expert_id)
    profile = build_expert_profile(expert, careers=career_catalog)
    journey = build_expert_journey(expert)
    linked_careers = [c for c in career_catalog if c.id in expert.career_ids]
    knowledge = build_expert_knowledge(expert, linked_careers=linked_careers)
    upcoming_events = await events.list_career_events(mentor_id=expert_id)

    return ExpertDetailDTO(
        id=profile.id, name=profile.name, role_type=profile.role_type,
        profession=profile.profession, specialization=profile.specialization,
        field=profile.field, bio=profile.bio, country=profile.country, city=profile.city,
        industries=profile.industries, education=profile.education,
        organization=profile.organization, current_role=profile.current_role,
        years_experience=profile.years_experience, languages=profile.languages,
        photo_url=profile.photo_url, who_should_talk_to_me=profile.who_should_talk_to_me,
        trait_tags=profile.trait_tags, learning_style_fit=profile.learning_style_fit,
        linked_careers=profile.linked_careers,
        career_journey=[
            CareerJourneyMilestoneDTO(
                stage=m.stage, label=m.label, description=m.description, year_label=m.year_label,
            )
            for m in journey
        ],
        day_in_the_life=expert.day_in_the_life, weekly_routine=expert.weekly_routine,
        biggest_challenges=expert.biggest_challenges, favourite_part=expert.favourite_part,
        biggest_misconceptions=expert.biggest_misconceptions,
        what_surprised_them=expert.what_surprised_them, biggest_mistake=expert.biggest_mistake,
        one_regret=expert.one_regret, salary_reality=expert.salary_reality,
        work_life_balance=expert.work_life_balance,
        advice_for_beginners=expert.advice_for_beginners, advice_for_parents=expert.advice_for_parents,
        faqs=[CareerFAQDTO(question=f.question, answer=f.answer) for f in expert.faqs],
        projects=knowledge.projects, research=knowledge.research,
        certifications=knowledge.certifications, conferences=knowledge.conferences,
        organizations=knowledge.organizations, volunteer_work=knowledge.volunteer_work,
        portfolio_links=[LinkRefDTO(label=lr.label, url=lr.url) for lr in knowledge.portfolio_links],
        social_links=[LinkRefDTO(label=lr.label, url=lr.url) for lr in knowledge.social_links],
        daily_skills=knowledge.daily_skills, daily_tools=knowledge.daily_tools,
        recommended_books=knowledge.recommended_books,
        recommended_communities=knowledge.recommended_communities,
        suggested_books=knowledge.suggested_books, suggested_companies=knowledge.suggested_companies,
        suggested_certifications=knowledge.suggested_certifications,
        available_slots=generate_available_slots(),
        upcoming_career_talks=[
            CareerEventDTO(
                id=e.id, title=e.title, event_type=e.event_type, institution_id=e.institution_id,
                mentor_id=e.mentor_id, description=e.description, scheduled_at=e.scheduled_at,
            )
            for e in upcoming_events
        ],
        updated_at=expert.updated_at,
        accepts_mentorship=expert.accepts_mentorship, max_students=expert.max_students,
        current_mentee_count=current_mentee_count,
    )
