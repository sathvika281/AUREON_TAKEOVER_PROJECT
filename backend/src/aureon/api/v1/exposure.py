from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_career_world_repository,
    get_expert_repository,
    get_experiment_repository,
    get_journey_story_repository,
    get_knowledge_circle_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.models.career import CareerStory
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.domain.services.career_view import build_career_summary_dto
from aureon.domain.services.exposure_recommendation import record_exposure_interaction
from aureon.domain.services.exposure_universe_service import (
    ExposureMap,
    ExposurePossibility,
    MissingWorldCard,
    WorldExplorationDetail,
    build_exposure_universe,
    build_world_detail,
)
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.career_world_repository import CareerWorldRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.journey_story_repository import JourneyStoryRepository
from aureon.services.supabase.repositories.knowledge_circle_repository import KnowledgeCircleRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CareerWorldDTO,
    ExperimentSummaryDTO,
    ExpertSummaryDTO,
    ExposureInteractionRequest,
    ExposureInteractionResponse,
    ExposureMapDTO,
    ExposureSuggestionDTO,
    ExposureUniverseResponse,
    KnowledgeCircleSummaryDTO,
    MissingWorldCardDTO,
    WorldExplorationDetailDTO,
    WorldExposureSummaryDTO,
    WorldRelatedStoryDTO,
)

router = APIRouter(prefix="/students", tags=["exposure-universe"], dependencies=[Depends(require_own_profile)])


def _world_dto(world: CareerWorld) -> CareerWorldDTO:
    return CareerWorldDTO(
        id=world.id, name=world.name, description=world.description, why_it_matters=world.why_it_matters,
        global_importance=world.global_importance, future_growth=world.future_growth,
        famous_careers=world.famous_careers, beginner_roadmap=world.beginner_roadmap,
        required_skills=world.required_skills, misconceptions=world.misconceptions,
        related_industries=world.related_industries, videos=world.videos, books=world.books,
        communities=world.communities, beginner_projects=world.beginner_projects,
        internships=world.internships, colleges=world.colleges, companies=world.companies,
        source_note=world.source_note,
    )


def _circle_summary_dto(circle: KnowledgeCircle) -> KnowledgeCircleSummaryDTO:
    return KnowledgeCircleSummaryDTO(id=circle.id, name=circle.name, overview=circle.overview)


def _story_preview_dto(story: CareerStory, *, career_name: str) -> WorldRelatedStoryDTO:
    return WorldRelatedStoryDTO(
        id=story.id, career_id=story.career_id, career_name=career_name,
        person_label=story.person_label, journey=story.journey, advice=story.advice,
    )


def _expose_map_dto(exposure_map: ExposureMap) -> ExposureMapDTO:
    return ExposureMapDTO(
        engaged=[WorldExposureSummaryDTO(world_name=s.world_name, level=s.level) for s in exposure_map.engaged],
        limited_or_none=[
            WorldExposureSummaryDTO(world_name=s.world_name, level=s.level) for s in exposure_map.limited_or_none
        ],
    )


def _missing_world_card_dto(card: MissingWorldCard) -> MissingWorldCardDTO:
    return MissingWorldCardDTO(
        world=_world_dto(card.world), level=card.level, match_count=card.match_count,
        why_missing=card.why_missing,
        related_careers=[build_career_summary_dto(c) for c in card.related_careers],
        linked_circle=_circle_summary_dto(card.linked_circle) if card.linked_circle else None,
    )


def _suggestion_dto(possibility: ExposurePossibility) -> ExposureSuggestionDTO:
    career = possibility.career
    enrichment = possibility.enrichment
    return ExposureSuggestionDTO(
        career=build_career_summary_dto(career),
        curiosity_hook=possibility.curiosity_hook,
        mini_introduction=enrichment.mini_introduction,
        quick_project=enrichment.quick_project,
        watch=enrichment.watch,
        read=enrichment.read,
        build=enrichment.build,
        join=enrichment.join,
        reflect_prompt=enrichment.reflect_prompt,
        suggested_experience=(
            ExperimentSummaryDTO(
                id=enrichment.suggested_experience.id, title=enrichment.suggested_experience.title,
                related_world=enrichment.suggested_experience.related_world,
                estimated_minutes=enrichment.suggested_experience.estimated_minutes,
            )
            if enrichment.suggested_experience else None
        ),
        related_missing_world=possibility.related_missing_world,
    )


def _expert_summary_dto(expert) -> ExpertSummaryDTO:
    return ExpertSummaryDTO(
        id=expert.id, name=expert.name, profession=expert.profession,
        specialization=expert.specialization, country=expert.country, city=expert.city,
        years_experience=expert.years_experience, industries=expert.industries,
        organization=expert.organization, trait_tags=expert.trait_tags,
        who_should_talk_to_me=expert.who_should_talk_to_me, photo_url=expert.photo_url,
        updated_at=expert.updated_at,
    )


def _world_detail_dto(detail: WorldExplorationDetail) -> WorldExplorationDetailDTO:
    careers_by_id = {c.id: c for c in detail.related_careers}
    return WorldExplorationDetailDTO(
        world=_world_dto(detail.world), level=detail.level, match_count=detail.match_count,
        why_missing=detail.why_missing,
        related_careers=[build_career_summary_dto(c) for c in detail.related_careers],
        related_stories=[
            _story_preview_dto(s, career_name=careers_by_id[s.career_id].name if s.career_id in careers_by_id else "")
            for s in detail.related_stories
        ],
        related_experts=[_expert_summary_dto(e) for e in detail.related_experts],
        linked_circle=_circle_summary_dto(detail.linked_circle) if detail.linked_circle else None,
    )


@router.get("/{student_id}/exposure-universe", response_model=ExposureUniverseResponse)
async def get_exposure_universe(
    student_id: str,
    careers: CareerRepository = Depends(get_career_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    experiments: ExperimentRepository = Depends(get_experiment_repository),
    worlds_repo: CareerWorldRepository = Depends(get_career_world_repository),
    circles_repo: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
) -> ExposureUniverseResponse:
    """The unified Exposure Universe response — composes Missing Worlds
    detection (missing_worlds_engine.py, via exposure_universe_service.py)
    with Exposure Universe's own unfamiliar-possibility selection
    (exposure_recommendation.py) into one screen's worth of data. See
    domain/services/exposure_universe_service.py for the composition."""
    profile = await profiles.get_or_create(student_id)
    catalog = await careers.list_careers()
    experiment_catalog = await experiments.list_experiments()
    worlds = await worlds_repo.list_worlds()
    circles = await circles_repo.list_circles()

    universe = build_exposure_universe(
        profile=profile, worlds=worlds, careers=catalog, experiments=experiment_catalog,
        knowledge_circles=circles, now=datetime.now(timezone.utc),
    )
    await profiles.save(profile)

    return ExposureUniverseResponse(
        exposure_map=_expose_map_dto(universe.exposure_map),
        missing_worlds=[_missing_world_card_dto(c) for c in universe.missing_worlds],
        suggestions=[_suggestion_dto(p) for p in universe.possibilities],
    )


@router.get("/{student_id}/exposure-universe/worlds/{world_id}", response_model=WorldExplorationDetailDTO)
async def get_exposure_universe_world_detail(
    student_id: str,
    world_id: str,
    careers: CareerRepository = Depends(get_career_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    worlds_repo: CareerWorldRepository = Depends(get_career_world_repository),
    circles_repo: KnowledgeCircleRepository = Depends(get_knowledge_circle_repository),
    stories_repo: JourneyStoryRepository = Depends(get_journey_story_repository),
    experts_repo: ExpertRepository = Depends(get_expert_repository),
) -> WorldExplorationDetailDTO:
    """The "Explore a World" deep-dive — a single world's full detail
    (careers/stories/experts/circle), kept out of the main list response
    since every list request returning every world's full detail would be
    wasteful."""
    profile = await profiles.get_or_create(student_id)
    catalog = await careers.list_careers()
    worlds = await worlds_repo.list_worlds()
    circles = await circles_repo.list_circles()

    detail = await build_world_detail(
        world_id=world_id, profile=profile, worlds=worlds, careers=catalog,
        knowledge_circles=circles, stories=stories_repo, experts=experts_repo,
    )
    if detail is None:
        raise HTTPException(status_code=404, detail="World not found")
    return _world_detail_dto(detail)


@router.post("/{student_id}/exposure-universe/interact", response_model=ExposureInteractionResponse)
async def record_exposure_universe_interaction(
    student_id: str,
    body: ExposureInteractionRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ExposureInteractionResponse:
    profile = await profiles.get_or_create(student_id)
    record_exposure_interaction(
        profile, career_id=body.career_id, interaction=body.interaction, now=datetime.now(timezone.utc)
    )
    await profiles.save(profile)
    return ExposureInteractionResponse(recorded=True)
