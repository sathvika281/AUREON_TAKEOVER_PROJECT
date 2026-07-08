from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.domain.services.career_exploration import record_exploration_event
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CareerExplorationEventDTO,
    CareerExplorationHistoryResponse,
    RecordCareerExplorationEventRequest,
    RecordCareerExplorationEventResponse,
)

router = APIRouter(prefix="/students", tags=["career-exploration"], dependencies=[Depends(require_own_profile)])


@router.post(
    "/{student_id}/career-exploration-events",
    response_model=RecordCareerExplorationEventResponse,
)
async def record_career_exploration_event(
    student_id: str,
    request: RecordCareerExplorationEventRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> RecordCareerExplorationEventResponse:
    """Records one observed exploration interaction (opened, bookmarked,
    story viewed, etc.) — observational only, never itself treated as
    evidence. Near-instant duplicates of the same career+interaction are
    silently skipped (see ``career_exploration.py``'s dedup window);
    genuine repeat interactions over time are always recorded.
    """
    profile = await profiles.get_or_create(student_id)
    event = record_exploration_event(
        profile,
        career_id=request.career_id,
        interaction_type=request.interaction_type,
        metadata=request.metadata,
        now=datetime.now(timezone.utc),
    )
    if event is not None:
        profile.updated_at = event.created_at
        await profiles.save(profile)
    return RecordCareerExplorationEventResponse(recorded=event is not None)


@router.get(
    "/{student_id}/career-exploration-history",
    response_model=CareerExplorationHistoryResponse,
)
async def get_career_exploration_history(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerExplorationHistoryResponse:
    """Reads persisted exploration history only, most recent first —
    survives refresh/new device, same pattern as the rest of the profile."""
    profile = await profiles.get_or_create(student_id)
    ordered = sorted(profile.career_exploration_history, key=lambda e: e.created_at, reverse=True)
    return CareerExplorationHistoryResponse(
        events=[
            CareerExplorationEventDTO(
                id=e.id,
                career_id=e.career_id,
                interaction_type=e.interaction_type,
                metadata=e.metadata,
                created_at=e.created_at,
            )
            for e in ordered
        ]
    )
