from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_career_event_repository, get_mentor_repository
from aureon.domain.services.career_experience_view import generate_available_slots
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.shared.schemas import CareerEventDTO, MentorDetailDTO, MentorSummaryDTO

router = APIRouter(prefix="/mentors", tags=["mentors"])


def _summary_dto(m) -> MentorSummaryDTO:
    return MentorSummaryDTO(
        id=m.id, name=m.name, role_type=m.role_type, field=m.field,
        bio=m.bio, trait_tags=m.trait_tags, learning_style_fit=m.learning_style_fit,
        organization=m.organization, years_experience=m.years_experience,
        journey_highlights=m.journey_highlights, discussion_topics=m.discussion_topics,
    )


@router.get("", response_model=list[MentorSummaryDTO])
async def list_mentors(
    role_type: str | None = None,
    field: str | None = None,
    mentors: MentorRepository = Depends(get_mentor_repository),
) -> list[MentorSummaryDTO]:
    """Mentor Knowledge Base browse endpoint — always open, no gating.
    Every mentor here is a real "expert" for Expert Connect (V13) — no
    separate parallel Expert model."""
    results = await mentors.list_mentors(role_type=role_type, field=field)
    return [_summary_dto(m) for m in results]


@router.get("/{mentor_id}", response_model=MentorDetailDTO)
async def get_mentor_detail(
    mentor_id: str,
    mentors: MentorRepository = Depends(get_mentor_repository),
    events: CareerEventRepository = Depends(get_career_event_repository),
) -> MentorDetailDTO:
    """V13 — the mentor-detail route that never existed before. Real
    seeded career talks this mentor hosts + deterministically-generated
    (never fabricated-as-real) available slots."""
    mentor = await mentors.get_mentor(mentor_id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")

    upcoming_events = await events.list_career_events(mentor_id=mentor_id)
    summary = _summary_dto(mentor)

    return MentorDetailDTO(
        **summary.model_dump(),
        available_slots=generate_available_slots(),
        upcoming_career_talks=[
            CareerEventDTO(
                id=e.id, title=e.title, event_type=e.event_type, institution_id=e.institution_id,
                mentor_id=e.mentor_id, description=e.description, scheduled_at=e.scheduled_at,
            )
            for e in upcoming_events
        ],
    )
