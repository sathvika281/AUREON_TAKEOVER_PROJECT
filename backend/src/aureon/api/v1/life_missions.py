from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from aureon.api.deps import get_life_mission_repository, get_student_profile_repository, require_own_profile
from aureon.domain.services.life_mission_engine import analyze_life_missions
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    LifeMissionDTO,
    LifeMissionsResponse,
    MissionEvidenceItemDTO,
    MissionResonanceDTO,
)

router = APIRouter(prefix="/students", tags=["life-missions"], dependencies=[Depends(require_own_profile)])


def _mission_dto(mission) -> LifeMissionDTO:
    return LifeMissionDTO(
        id=mission.id, name=mission.name, description=mission.description,
        famous_people=mission.famous_people, organizations=mission.organizations,
        companies=mission.companies, nonprofits=mission.nonprofits, books=mission.books,
        documentaries=mission.documentaries, podcasts=mission.podcasts, communities=mission.communities,
        real_world_examples=mission.real_world_examples, suggested_careers=mission.suggested_careers,
        projects=mission.projects, volunteering_opportunities=mission.volunteering_opportunities,
        research_areas=mission.research_areas, startup_ideas=mission.startup_ideas,
        source_note=mission.source_note,
    )


@router.get("/{student_id}/life-missions", response_model=LifeMissionsResponse)
async def get_life_missions(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    missions_repo: LifeMissionRepository = Depends(get_life_mission_repository),
) -> LifeMissionsResponse:
    """Infers which real-world-impact missions the student resonates
    with from real accumulated evidence — computed fresh, never a
    fabricated score. See domain/services/life_mission_engine.py."""
    profile = await profiles.get_or_create(student_id)
    missions = await missions_repo.list_missions()

    resonances = analyze_life_missions(profile, missions, now=datetime.now(timezone.utc))
    resonant_ids = {r.mission.id for r in resonances}

    return LifeMissionsResponse(
        resonances=[
            MissionResonanceDTO(
                mission=_mission_dto(r.mission), tier=r.tier, trend=r.trend, explanation=r.explanation,
                evidence=[
                    MissionEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
                    for e in r.evidence
                ],
            )
            for r in resonances
        ],
        other_missions=[_mission_dto(m) for m in missions if m.id not in resonant_ids],
    )
