from fastapi import APIRouter, Depends

from aureon.api.deps import (
    get_career_repository,
    get_career_world_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.missing_worlds_engine import analyze_missing_worlds
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.career_world_repository import CareerWorldRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import CareerWorldDTO, MissingWorldsResponse, WorldExplorationDTO

router = APIRouter(prefix="/students", tags=["missing-worlds"], dependencies=[Depends(require_own_profile)])


def _world_dto(world) -> CareerWorldDTO:
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


@router.get("/{student_id}/missing-worlds", response_model=MissingWorldsResponse)
async def get_missing_worlds(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    worlds_repo: CareerWorldRepository = Depends(get_career_world_repository),
    careers_repo: CareerRepository = Depends(get_career_repository),
) -> MissingWorldsResponse:
    """Classifies every career world the student has explored, partially
    explored, or never encountered — computed fresh from real
    accumulated evidence. See domain/services/missing_worlds_engine.py."""
    profile = await profiles.get_or_create(student_id)
    worlds = await worlds_repo.list_worlds()
    careers = await careers_repo.list_careers()

    analysis = analyze_missing_worlds(profile, worlds, careers)

    return MissingWorldsResponse(
        worlds=[
            WorldExplorationDTO(world=_world_dto(e.world), exploration_level=e.level, match_count=e.match_count)
            for e in analysis.explorations
        ],
        recommended_next=[w.id for w in analysis.recommended_next],
    )
