from fastapi import APIRouter, Depends

from aureon.api.deps import get_career_event_repository
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.shared.schemas import CareerEventDTO, CareerEventsResponse

router = APIRouter(prefix="/career-events", tags=["career-events"])


@router.get("", response_model=CareerEventsResponse)
async def list_career_events(
    institution_id: str | None = None,
    mentor_id: str | None = None,
    events: CareerEventRepository = Depends(get_career_event_repository),
) -> CareerEventsResponse:
    """Experience Events browse endpoint — always open, no gating. Same
    shared Knowledge Base for institution-hosted (workshops/hackathons/
    open days) and mentor-hosted (career talks) events."""
    results = await events.list_career_events(institution_id=institution_id, mentor_id=mentor_id)
    return CareerEventsResponse(events=[
        CareerEventDTO(
            id=e.id, title=e.title, event_type=e.event_type, institution_id=e.institution_id,
            mentor_id=e.mentor_id, description=e.description, scheduled_at=e.scheduled_at,
        )
        for e in results
    ])
