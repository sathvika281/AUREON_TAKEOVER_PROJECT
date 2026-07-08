from fastapi import APIRouter, Depends

from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.domain.services.history_view import build_history_items
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import HistoryItemDTO, HistoryResponse

router = APIRouter(prefix="/students", tags=["history"], dependencies=[Depends(require_own_profile)])


@router.get("/{student_id}/history", response_model=HistoryResponse)
async def get_history(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> HistoryResponse:
    """Investigation History (V12) — a pure read-aggregation over every
    already-persisted investigation/comparison/simulation/match. Never
    regenerates anything; selecting an item elsewhere fetches that
    feature's own already-persisted record by id."""
    profile = await profiles.get_or_create(student_id)
    items = build_history_items(profile)
    return HistoryResponse(items=[
        HistoryItemDTO(
            id=i.id, mission_name=i.mission_name, mission_type=i.mission_type,
            owning_specialist=i.owning_specialist, timestamp=i.timestamp,
            status=i.status, artifact_id=i.artifact_id,
        )
        for i in items
    ])
