from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_event_repository,
    get_mentor_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.career_experience_actions import (
    add_event_registration,
    add_expert_session_booking,
    add_guidance_request,
    save_expert,
    unsave_expert,
)
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    BookExpertSessionRequest,
    EventRegistrationDTO,
    EventRegistrationsResponse,
    ExpertSessionBookingDTO,
    ExpertSessionBookingsResponse,
    GuidanceRequestDTO,
    GuidanceRequestsResponse,
    RegisterForEventRequest,
    RequestGuidanceRequest,
    SavedExpertsResponse,
)

router = APIRouter(prefix="/students", tags=["career-experience"], dependencies=[Depends(require_own_profile)])


def _bookings_response(profile) -> ExpertSessionBookingsResponse:
    return ExpertSessionBookingsResponse(bookings=[
        ExpertSessionBookingDTO(
            id=b.id, mentor_id=b.mentor_id, mentor_name=b.mentor_name,
            slot_start=b.slot_start, topic=b.topic, created_at=b.created_at,
        )
        for b in profile.expert_session_bookings
    ])


def _guidance_response(profile) -> GuidanceRequestsResponse:
    return GuidanceRequestsResponse(requests=[
        GuidanceRequestDTO(
            id=r.id, mentor_id=r.mentor_id, mentor_name=r.mentor_name,
            message=r.message, status=r.status, created_at=r.created_at,
        )
        for r in profile.guidance_requests
    ])


def _registrations_response(profile) -> EventRegistrationsResponse:
    return EventRegistrationsResponse(registrations=[
        EventRegistrationDTO(id=r.id, event_id=r.event_id, event_title=r.event_title, created_at=r.created_at)
        for r in profile.event_registrations
    ])


@router.post("/{student_id}/expert-sessions/book", response_model=ExpertSessionBookingsResponse)
async def book_expert_session(
    student_id: str,
    request: BookExpertSessionRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    mentors: MentorRepository = Depends(get_mentor_repository),
) -> ExpertSessionBookingsResponse:
    """A real, student-initiated request to meet an expert at a specific
    (deterministically generated, illustrative) time — never simulated as
    auto-accepted; no real video-calling/calendar integration exists."""
    mentor = await mentors.get_mentor(request.mentor_id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")

    profile = await profiles.get_or_create(student_id)
    add_expert_session_booking(profile, mentor, slot_start=request.slot_start, topic=request.topic)
    await profiles.save(profile)
    return _bookings_response(profile)


@router.get("/{student_id}/expert-sessions", response_model=ExpertSessionBookingsResponse)
async def get_expert_sessions(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> ExpertSessionBookingsResponse:
    profile = await profiles.get_or_create(student_id)
    return _bookings_response(profile)


@router.post("/{student_id}/expert-guidance-requests", response_model=GuidanceRequestsResponse)
async def request_guidance(
    student_id: str,
    request: RequestGuidanceRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    mentors: MentorRepository = Depends(get_mentor_repository),
) -> GuidanceRequestsResponse:
    """A lighter alternative to booking a specific slot."""
    mentor = await mentors.get_mentor(request.mentor_id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")

    profile = await profiles.get_or_create(student_id)
    add_guidance_request(profile, mentor, message=request.message)
    await profiles.save(profile)
    return _guidance_response(profile)


@router.get("/{student_id}/expert-guidance-requests", response_model=GuidanceRequestsResponse)
async def get_guidance_requests(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> GuidanceRequestsResponse:
    profile = await profiles.get_or_create(student_id)
    return _guidance_response(profile)


@router.post("/{student_id}/saved-experts/{mentor_id}", response_model=SavedExpertsResponse)
async def save_expert_route(
    student_id: str,
    mentor_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> SavedExpertsResponse:
    """No complex backend logic — a minimal, idempotent bookmark list."""
    profile = await profiles.get_or_create(student_id)
    mentor_ids = save_expert(profile, mentor_id)
    await profiles.save(profile)
    return SavedExpertsResponse(mentor_ids=mentor_ids)


@router.delete("/{student_id}/saved-experts/{mentor_id}", response_model=SavedExpertsResponse)
async def unsave_expert_route(
    student_id: str,
    mentor_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> SavedExpertsResponse:
    profile = await profiles.get_or_create(student_id)
    mentor_ids = unsave_expert(profile, mentor_id)
    await profiles.save(profile)
    return SavedExpertsResponse(mentor_ids=mentor_ids)


@router.get("/{student_id}/saved-experts", response_model=SavedExpertsResponse)
async def get_saved_experts(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> SavedExpertsResponse:
    profile = await profiles.get_or_create(student_id)
    return SavedExpertsResponse(mentor_ids=profile.saved_experts)


@router.post("/{student_id}/events/register", response_model=EventRegistrationsResponse)
async def register_for_event(
    student_id: str,
    request: RegisterForEventRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    events: CareerEventRepository = Depends(get_career_event_repository),
) -> EventRegistrationsResponse:
    event = await events.get_career_event(request.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    profile = await profiles.get_or_create(student_id)
    if add_event_registration(profile, event_id=event.id, event_title=event.title) is not None:
        await profiles.save(profile)
    return _registrations_response(profile)


@router.get("/{student_id}/events/registrations", response_model=EventRegistrationsResponse)
async def get_event_registrations(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> EventRegistrationsResponse:
    profile = await profiles.get_or_create(student_id)
    return _registrations_response(profile)
