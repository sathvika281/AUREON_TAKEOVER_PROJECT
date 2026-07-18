from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_expert_repository, get_mentorship_repository, require_own_profile
from aureon.domain.services.mentorship_service import (
    accept,
    add_note,
    complete,
    count_active_mentees,
    decline,
    has_active_mentorship,
    is_eligible_for_mentorship,
    request_mentorship,
)
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.mentorship_repository import MentorshipRepository
from aureon.shared.schemas import (
    AddMentorshipNoteRequest,
    MentorshipDTO,
    MentorshipProgressNoteDTO,
    MentorshipsResponse,
    RequestMentorshipRequest,
)

# The expert's only way into a mentorship request is the opaque
# review_token — there is no expert-side login anywhere in this system
# to gate a "real" authenticated accept/decline behind. Kept open,
# mirroring `/shared-sessions/{access_token}` exactly.
router = APIRouter(tags=["mentorship"])

# Student-scoped — requesting/listing/completing your own mentorships
# genuinely needs the caller to be the authenticated student.
student_router = APIRouter(
    prefix="/students", tags=["mentorship"], dependencies=[Depends(require_own_profile)]
)


def _mentorship_dto(mentorship, expert=None) -> MentorshipDTO:
    return MentorshipDTO(
        id=mentorship.id, student_id=mentorship.student_id, expert_id=mentorship.expert_id,
        review_token=mentorship.review_token, status=mentorship.status, goals=mentorship.goals,
        progress_notes=[
            MentorshipProgressNoteDTO(id=n.id, author_role=n.author_role, note=n.note, created_at=n.created_at)
            for n in mentorship.progress_notes
        ],
        created_at=mentorship.created_at, updated_at=mentorship.updated_at,
        expert_name=expert.name if expert else "",
        expert_role=expert.current_role if expert else "",
        expert_domain=expert.field if expert else "",
    )


@student_router.post("/{student_id}/mentorships", response_model=MentorshipDTO)
async def create_mentorship_request(
    student_id: str,
    body: RequestMentorshipRequest,
    experts: ExpertRepository = Depends(get_expert_repository),
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    expert = await experts.get_expert(body.expert_id)
    if expert is None:
        raise HTTPException(status_code=404, detail="Expert not found")

    existing = await mentorships.list_for_student(student_id)
    if has_active_mentorship(existing, expert.id):
        raise HTTPException(status_code=400, detail="You already have an active mentorship request with this expert.")

    current_mentee_count = count_active_mentees(await mentorships.list_for_expert(expert.id), expert.id)
    if not is_eligible_for_mentorship(expert, current_mentee_count):
        raise HTTPException(status_code=400, detail="This expert isn't available for new mentorship requests right now.")

    mentorship = request_mentorship(student_id=student_id, expert=expert, goals=body.goals)
    saved = await mentorships.create(mentorship)
    return _mentorship_dto(saved, expert)


@student_router.get("/{student_id}/mentorships", response_model=MentorshipsResponse)
async def list_my_mentorships(
    student_id: str,
    experts: ExpertRepository = Depends(get_expert_repository),
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipsResponse:
    results = await mentorships.list_for_student(student_id)
    experts_by_id = {}
    for expert_id in {m.expert_id for m in results}:
        expert = await experts.get_expert(expert_id)
        if expert is not None:
            experts_by_id[expert_id] = expert
    return MentorshipsResponse(
        mentorships=[_mentorship_dto(m, experts_by_id.get(m.expert_id)) for m in results]
    )


@student_router.post("/{student_id}/mentorships/{mentorship_id}/notes", response_model=MentorshipDTO)
async def add_student_mentorship_note(
    student_id: str,
    mentorship_id: str,
    body: AddMentorshipNoteRequest,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_id(mentorship_id)
    if mentorship is None or mentorship.student_id != student_id:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    updated = add_note(mentorship, author_role=body.author_role, note=body.note)
    saved = await mentorships.update(updated)
    return _mentorship_dto(saved)


@student_router.post("/{student_id}/mentorships/{mentorship_id}/complete", response_model=MentorshipDTO)
async def complete_mentorship_as_student(
    student_id: str,
    mentorship_id: str,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_id(mentorship_id)
    if mentorship is None or mentorship.student_id != student_id:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    saved = await mentorships.update(complete(mentorship))
    return _mentorship_dto(saved)


@router.get("/mentorship-review/{review_token}", response_model=MentorshipDTO)
async def get_mentorship_for_review(
    review_token: str,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    """The expert's only way in — deliberately no auth check beyond
    holding the token, same discipline as `get_shared_session`."""
    mentorship = await mentorships.get_by_token(review_token)
    if mentorship is None:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    return _mentorship_dto(mentorship)


@router.post("/mentorship-review/{review_token}/accept", response_model=MentorshipDTO)
async def accept_mentorship(
    review_token: str,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_token(review_token)
    if mentorship is None:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    saved = await mentorships.update(accept(mentorship))
    return _mentorship_dto(saved)


@router.post("/mentorship-review/{review_token}/decline", response_model=MentorshipDTO)
async def decline_mentorship(
    review_token: str,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_token(review_token)
    if mentorship is None:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    saved = await mentorships.update(decline(mentorship))
    return _mentorship_dto(saved)


@router.post("/mentorship-review/{review_token}/notes", response_model=MentorshipDTO)
async def add_expert_mentorship_note(
    review_token: str,
    body: AddMentorshipNoteRequest,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_token(review_token)
    if mentorship is None:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    updated = add_note(mentorship, author_role=body.author_role, note=body.note)
    saved = await mentorships.update(updated)
    return _mentorship_dto(saved)


@router.post("/mentorship-review/{review_token}/complete", response_model=MentorshipDTO)
async def complete_mentorship_as_expert(
    review_token: str,
    mentorships: MentorshipRepository = Depends(get_mentorship_repository),
) -> MentorshipDTO:
    mentorship = await mentorships.get_by_token(review_token)
    if mentorship is None:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    saved = await mentorships.update(complete(mentorship))
    return _mentorship_dto(saved)
