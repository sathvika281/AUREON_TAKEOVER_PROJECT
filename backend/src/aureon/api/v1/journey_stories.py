from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_expert_repository,
    get_journey_story_repository,
    get_life_mission_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.journey_story_service import (
    build_journey_story_view,
    personalize_stories,
    record_story_reflection,
)
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.journey_story_repository import JourneyStoryRepository
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.student_profile_repository import StudentProfileRepository
from aureon.shared.schemas import (
    CareerJourneyMilestoneDTO,
    CareerSummaryDTO,
    JourneyStoryDTO,
    JourneyStoryFiltersResponse,
    JourneyStorySearchResponse,
    LinkedExpertRefDTO,
    ReflectOnJourneyStoryRequest,
    ReflectOnJourneyStoryResponse,
    RelevantJourneyStoriesResponse,
)

router = APIRouter(prefix="/journey-stories", tags=["journey-stories"])

#: The standalone Journey Stories screen's default, student-facing content —
#: illustrative student self-discovery narratives only. Professional/
#: workplace stories (story_type="composite"/"publicly_documented") stay
#: exclusively on the career detail page's "Human Stories" section (see
#: career_repository.py::list_stories_for_career). An explicit `story_type`
#: query param still overrides this default for tooling/back-compat.
DEFAULT_STANDALONE_STORY_TYPE = "composite_student_discovery"

# Student-scoped — reflecting on a story and seeing personalized
# "relate to" ordering genuinely need the caller to be the authenticated
# student, unlike the open directory below.
student_router = APIRouter(
    prefix="/students", tags=["journey-stories"], dependencies=[Depends(require_own_profile)]
)


async def _story_dto(
    story, *, careers: CareerRepository, experts: ExpertRepository, missions: LifeMissionRepository
) -> JourneyStoryDTO:
    career = await careers.get_career(story.career_id)
    linked_expert = await experts.get_expert(story.linked_expert_id) if story.linked_expert_id else None
    linked_mission = await missions.get_mission(story.linked_life_mission_id) if story.linked_life_mission_id else None
    view = build_journey_story_view(story, career=career, linked_expert=linked_expert, linked_mission=linked_mission)
    return JourneyStoryDTO(
        id=view.id, career_id=view.career_id, career_name=view.career_name,
        person_label=view.person_label, background=view.background, journey=view.journey,
        challenges=view.challenges, turning_points=view.turning_points, advice=view.advice,
        lessons_learned=view.lessons_learned, trait_tags=view.trait_tags,
        timeline=[
            CareerJourneyMilestoneDTO(stage=m.stage, label=m.label, description=m.description, year_label=m.year_label)
            for m in view.timeline
        ],
        career_switch=view.career_switch, gap_year=view.gap_year,
        uncertainty_period=view.uncertainty_period, current_outcome=view.current_outcome,
        industry=view.industry, story_type=view.story_type, source_reference=view.source_reference,
        discovery_themes=view.discovery_themes,
        linked_expert=(
            LinkedExpertRefDTO(id=view.linked_expert.id, name=view.linked_expert.name, profession=view.linked_expert.profession)
            if view.linked_expert
            else None
        ),
        linked_life_mission_name=view.linked_life_mission_name,
    )


@router.get("", response_model=JourneyStorySearchResponse)
async def search_journey_stories(
    q: str | None = None,
    career_id: str | None = None,
    industry: str | None = None,
    career_switch: bool | None = None,
    story_type: str | None = None,
    discovery_theme: str | None = None,
    limit: int = 100,
    offset: int = 0,
    stories: JourneyStoryRepository = Depends(get_journey_story_repository),
    careers: CareerRepository = Depends(get_career_repository),
    experts: ExpertRepository = Depends(get_expert_repository),
    missions: LifeMissionRepository = Depends(get_life_mission_repository),
) -> JourneyStorySearchResponse:
    """Journey Stories' directory endpoint — always open, no gating.
    Every story here is a real ``CareerStory`` row, honestly labeled via
    ``story_type``/``source_reference``. Defaults to student-discovery
    stories only; pass an explicit ``story_type`` to see other kinds
    (e.g. tooling, or a future admin view)."""
    effective_story_type = story_type if story_type is not None else DEFAULT_STANDALONE_STORY_TYPE
    results, total = await stories.search_stories(
        q=q, career_id=career_id, industry=industry, career_switch=career_switch,
        story_type=effective_story_type, discovery_theme=discovery_theme, limit=limit, offset=offset,
    )
    dtos = [await _story_dto(s, careers=careers, experts=experts, missions=missions) for s in results]
    return JourneyStorySearchResponse(stories=dtos, total=total, limit=limit, offset=offset)


@router.get("/filters", response_model=JourneyStoryFiltersResponse)
async def get_journey_story_filters(
    stories: JourneyStoryRepository = Depends(get_journey_story_repository),
    careers: CareerRepository = Depends(get_career_repository),
) -> JourneyStoryFiltersResponse:
    """Scoped to the same default story_type as search_journey_stories'
    default — a filter is never offered for content this screen doesn't
    actually show."""
    industries, career_ids, discovery_themes = await stories.list_filter_values(
        story_type=DEFAULT_STANDALONE_STORY_TYPE
    )
    career_catalog = await careers.list_careers()
    careers_by_id = {c.id: c for c in career_catalog}
    career_summaries = [
        CareerSummaryDTO(
            id=c.id, name=c.name, category=c.category, industry=c.industry,
            countries=c.countries, one_liner=c.one_liner, trait_tags=c.trait_tags,
        )
        for cid in career_ids
        if (c := careers_by_id.get(cid)) is not None
    ]
    return JourneyStoryFiltersResponse(industries=industries, careers=career_summaries, discovery_themes=discovery_themes)


@router.get("/{story_id}", response_model=JourneyStoryDTO)
async def get_journey_story(
    story_id: str,
    stories: JourneyStoryRepository = Depends(get_journey_story_repository),
    careers: CareerRepository = Depends(get_career_repository),
    experts: ExpertRepository = Depends(get_expert_repository),
    missions: LifeMissionRepository = Depends(get_life_mission_repository),
) -> JourneyStoryDTO:
    story = await stories.get_story(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Journey Story not found")
    return await _story_dto(story, careers=careers, experts=experts, missions=missions)


@student_router.get("/{student_id}/journey-stories/relevant", response_model=RelevantJourneyStoriesResponse)
async def get_relevant_journey_stories(
    student_id: str,
    stories: JourneyStoryRepository = Depends(get_journey_story_repository),
    careers: CareerRepository = Depends(get_career_repository),
    experts: ExpertRepository = Depends(get_expert_repository),
    missions: LifeMissionRepository = Depends(get_life_mission_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> RelevantJourneyStoriesResponse:
    """"Stories You May Relate To" — real, deterministic tag alignment
    against the student's own World Signals (see
    journey_story_service.py::personalize_stories); never shown when
    there's no genuine overlap."""
    profile = await profiles.get_or_create(student_id)
    all_stories, _total = await stories.search_stories(story_type="composite_student_discovery", limit=200)
    relevant = personalize_stories(all_stories, profile.discovery_onboarding.world_signals)
    dtos = [await _story_dto(s, careers=careers, experts=experts, missions=missions) for s in relevant]
    return RelevantJourneyStoriesResponse(stories=dtos)


@student_router.post(
    "/{student_id}/journey-stories/{story_id}/reflect", response_model=ReflectOnJourneyStoryResponse
)
async def reflect_on_journey_story(
    student_id: str,
    story_id: str,
    body: ReflectOnJourneyStoryRequest,
    stories: JourneyStoryRepository = Depends(get_journey_story_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ReflectOnJourneyStoryResponse:
    story = await stories.get_story(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Journey Story not found")
    profile = await profiles.get_or_create(student_id)
    record_story_reflection(profile, prompt=body.prompt, response=body.response, now=datetime.now(timezone.utc))
    await profiles.save(profile)
    return ReflectOnJourneyStoryResponse(recorded=True)
