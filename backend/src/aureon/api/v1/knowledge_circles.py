from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_career_world_repository,
    get_knowledge_circle_repository,
    get_life_mission_repository,
    get_student_profile_repository,
    get_topic_resource_repository,
    get_trend_repository,
    require_own_profile,
)
from aureon.domain.services.knowledge_circle_service import build_circle_view
from aureon.domain.services.resource_progress_service import (
    list_progress_for_circle,
    toggle_bookmark,
    toggle_completed,
)
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.career_world_repository import CareerWorldRepository
from aureon.services.supabase.repositories.knowledge_circle_repository import KnowledgeCircleRepository
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.student_profile_repository import StudentProfileRepository
from aureon.services.supabase.repositories.topic_resource_repository import TopicResourceRepository
from aureon.services.supabase.repositories.trend_repository import TrendRepository
from aureon.shared.schemas import (
    CircleProgressResponse,
    CircleResourceProgressDTO,
    KnowledgeCircleSummaryDTO,
    KnowledgeCircleViewDTO,
    ToggleCircleResourceRequest,
)

# Open — no gating, same catalog-browsing openness as /experts, /careers.
router = APIRouter(prefix="/knowledge-circles", tags=["knowledge-circles"])

# Student-scoped — bookmark/completion state is genuinely per-student.
student_router = APIRouter(
    prefix="/students", tags=["knowledge-circles"], dependencies=[Depends(require_own_profile)]
)


def _progress_dto(entry) -> CircleResourceProgressDTO:
    return CircleResourceProgressDTO(
        id=entry.id, circle_id=entry.circle_id, resource_type=entry.resource_type,
        resource_label=entry.resource_label, status=entry.status, updated_at=entry.updated_at,
    )


async def _view_dto(
    circle,
    *,
    career_worlds: CareerWorldRepository,
    topic_domains: TopicResourceRepository,
    careers: CareerRepository,
    trends: TrendRepository,
    missions: LifeMissionRepository,
) -> KnowledgeCircleViewDTO:
    career_world = await career_worlds.get_world(circle.linked_career_world_id) if circle.linked_career_world_id else None
    all_domains = await topic_domains.list_domains()
    matched_domains = [d for d in all_domains if d.id in circle.linked_topic_domain_ids]
    all_careers = await careers.list_careers()
    industries = {i.lower() for i in circle.related_career_industries}
    matched_careers = [c for c in all_careers if c.industry.lower() in industries]
    all_trends = await trends.list_trends()
    matched_trends = [t for t in all_trends if t.id in circle.related_trend_ids]
    all_missions = await missions.list_missions()
    matched_missions = [m for m in all_missions if m.id in circle.related_life_mission_ids]

    view = build_circle_view(
        circle, career_world=career_world, topic_domains=matched_domains,
        careers=matched_careers, trends=matched_trends, life_missions=matched_missions,
    )
    return KnowledgeCircleViewDTO(
        id=view.id, name=view.name, overview=view.overview,
        what_this_field_is_about=view.what_this_field_is_about,
        beginner_roadmap=view.beginner_roadmap, beginner_projects=view.beginner_projects,
        advanced_projects=view.advanced_projects, laboratories=view.laboratories,
        startups=view.startups, ngos=view.ngos, scholarships=view.scholarships,
        books=view.books, documentaries=view.documentaries, podcasts=view.podcasts,
        youtube_channels=view.youtube_channels, journals_and_newsletters=view.journals_and_newsletters,
        conferences=view.conferences, competitions=view.competitions, hackathons=view.hackathons,
        workshops=view.workshops, communities=view.communities,
        open_source_projects=view.open_source_projects, research_organizations=view.research_organizations,
        museums=view.museums, companies=view.companies, universities=view.universities,
        internships=view.internships, certifications=view.certifications,
        research_papers=view.research_papers, government_initiatives=view.government_initiatives,
        volunteering_opportunities=view.volunteering_opportunities,
    )


@router.get("", response_model=list[KnowledgeCircleSummaryDTO])
async def list_knowledge_circles(
    q: str | None = None,
    circles: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
) -> list[KnowledgeCircleSummaryDTO]:
    results = await circles.list_circles(q=q)
    return [KnowledgeCircleSummaryDTO(id=c.id, name=c.name, overview=c.overview) for c in results]


@router.get("/{circle_id}", response_model=KnowledgeCircleViewDTO)
async def get_knowledge_circle(
    circle_id: str,
    circles: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
    career_worlds: CareerWorldRepository = Depends(get_career_world_repository),
    topic_domains: TopicResourceRepository = Depends(get_topic_resource_repository),
    careers: CareerRepository = Depends(get_career_repository),
    trends: TrendRepository = Depends(get_trend_repository),
    missions: LifeMissionRepository = Depends(get_life_mission_repository),
) -> KnowledgeCircleViewDTO:
    circle = await circles.get_circle(circle_id)
    if circle is None:
        raise HTTPException(status_code=404, detail="Knowledge Circle not found")
    return await _view_dto(
        circle, career_worlds=career_worlds, topic_domains=topic_domains,
        careers=careers, trends=trends, missions=missions,
    )


@student_router.get(
    "/{student_id}/knowledge-circles/{circle_id}/progress", response_model=CircleProgressResponse
)
async def get_circle_progress(
    student_id: str,
    circle_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CircleProgressResponse:
    profile = await profiles.get_or_create(student_id)
    return CircleProgressResponse(progress=[_progress_dto(e) for e in list_progress_for_circle(profile, circle_id)])


@student_router.post(
    "/{student_id}/knowledge-circles/{circle_id}/bookmark", response_model=CircleProgressResponse
)
async def bookmark_circle_resource(
    student_id: str,
    circle_id: str,
    body: ToggleCircleResourceRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CircleProgressResponse:
    profile = await profiles.get_or_create(student_id)
    toggle_bookmark(
        profile, circle_id=circle_id, resource_type=body.resource_type, resource_label=body.resource_label
    )
    await profiles.save(profile)
    return CircleProgressResponse(progress=[_progress_dto(e) for e in list_progress_for_circle(profile, circle_id)])


@student_router.post(
    "/{student_id}/knowledge-circles/{circle_id}/complete", response_model=CircleProgressResponse
)
async def complete_circle_resource(
    student_id: str,
    circle_id: str,
    body: ToggleCircleResourceRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CircleProgressResponse:
    profile = await profiles.get_or_create(student_id)
    toggle_completed(
        profile, circle_id=circle_id, resource_type=body.resource_type, resource_label=body.resource_label
    )
    await profiles.save(profile)
    return CircleProgressResponse(progress=[_progress_dto(e) for e in list_progress_for_circle(profile, circle_id)])
