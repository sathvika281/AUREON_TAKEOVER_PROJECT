from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_expert_repository,
    get_parent_connect_repository,
    get_shared_session_repository,
    require_own_profile,
)
from aureon.domain.services.parent_connect_service import build_parent_career_view
from aureon.domain.services.shared_session_service import build_note, create_invite, join_as_participant
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.parent_connect_repository import ParentConnectRepository
from aureon.services.supabase.repositories.shared_session_repository import SharedSessionRepository
from aureon.shared.schemas import (
    AddSharedSessionNoteRequest,
    CareerFAQDTO,
    CreateSharedSessionRequest,
    JoinSharedSessionRequest,
    ParentCareerViewDTO,
    ParentExpertAdviceDTO,
    ParentQuestionDTO,
    ParentQuestionsResponse,
    SalaryRangeDTO,
    SharedSessionDTO,
    SharedSessionNoteDTO,
    SharedSessionsResponse,
    SharedSessionWithNotesDTO,
)

# Open routes — no auth, same openness as /mentors, /careers, /trends.
router = APIRouter(tags=["parent-connect"])

# The parent's/second-participant's only way into a session is the
# opaque access_token, so `/shared-sessions/{access_token}` must NOT
# require student auth — kept on the open router alongside it.

# Student-scoped routes (creating an invite, listing your own sessions)
# genuinely need the caller to be the authenticated student.
student_router = APIRouter(
    prefix="/students", tags=["parent-connect"], dependencies=[Depends(require_own_profile)]
)


def _session_dto(session) -> SharedSessionDTO:
    return SharedSessionDTO(
        id=session.id, student_id=session.student_id, mentor_id=session.mentor_id,
        career_id=session.career_id, access_token=session.access_token,
        participant_label=session.participant_label, topic=session.topic, status=session.status,
        scheduled_slot=session.scheduled_slot, created_at=session.created_at, updated_at=session.updated_at,
    )


@router.get("/careers/{career_id}/parent-view", response_model=ParentCareerViewDTO)
async def get_parent_career_view(
    career_id: str,
    language: str = "en",
    careers: CareerRepository = Depends(get_career_repository),
    guides: ParentConnectRepository = Depends(get_parent_connect_repository),
    experts: ExpertRepository = Depends(get_expert_repository),
) -> ParentCareerViewDTO:
    career = await careers.get_career(career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")

    guide = await guides.get_guide(career_id, language=language)
    all_experts, _total = await experts.search_experts(limit=500)
    experts_for_career = [e for e in all_experts if career_id in e.career_ids]

    view = build_parent_career_view(career, guide, experts_for_career)
    return ParentCareerViewDTO(
        career_id=view.career_id, career_name=view.career_name, one_liner=view.one_liner,
        required_education=view.required_education,
        salary_ranges=[SalaryRangeDTO(region=s.region, range=s.range, note=s.note) for s in view.salary_ranges],
        demand_2030=view.demand_2030, demand_2035=view.demand_2035, demand_2040=view.demand_2040,
        common_misconceptions=view.common_misconceptions, earning_reality=view.earning_reality,
        career_stability=view.career_stability, work_life_balance=view.work_life_balance,
        growth_opportunities=view.growth_opportunities, educational_pathways=view.educational_pathways,
        alternative_routes=view.alternative_routes, global_demand=view.global_demand,
        risks=view.risks, opportunities=view.opportunities,
        expert_advice=[
            ParentExpertAdviceDTO(
                expert_id=a.expert_id, expert_name=a.expert_name, expert_profession=a.expert_profession,
                advice_for_parents=a.advice_for_parents,
                faqs=[CareerFAQDTO(question=f.question, answer=f.answer) for f in a.faqs],
            )
            for a in view.expert_advice
        ],
    )


@router.get("/parent-questions", response_model=ParentQuestionsResponse)
async def list_parent_questions(
    category: str | None = None,
    career_id: str | None = None,
    language: str = "en",
    guides: ParentConnectRepository = Depends(get_parent_connect_repository),
) -> ParentQuestionsResponse:
    questions = await guides.list_questions(category=category, career_id=career_id, language=language)
    return ParentQuestionsResponse(
        questions=[
            ParentQuestionDTO(
                id=q.id, category=q.category, career_id=q.career_id, question=q.question,
                expert_response=q.expert_response, responding_expert_id=q.responding_expert_id,
                is_seeded=q.is_seeded, created_at=q.created_at,
            )
            for q in questions
        ]
    )


@router.get("/shared-sessions/{access_token}", response_model=SharedSessionWithNotesDTO)
async def get_shared_session(
    access_token: str,
    sessions: SharedSessionRepository = Depends(get_shared_session_repository),
) -> SharedSessionWithNotesDTO:
    """The second participant's (parent/guardian/teacher/etc.) only way
    in — deliberately no auth check beyond holding the token."""
    session = await sessions.get_by_token(access_token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    notes = await sessions.list_notes(session.id)
    return SharedSessionWithNotesDTO(
        **_session_dto(session).model_dump(),
        notes=[
            SharedSessionNoteDTO(
                id=n.id, session_id=n.session_id, author_role=n.author_role, note=n.note,
                created_at=n.created_at,
            )
            for n in notes
        ],
    )


@router.post("/shared-sessions/{access_token}/join", response_model=SharedSessionDTO)
async def join_shared_session(
    access_token: str,
    body: JoinSharedSessionRequest,
    sessions: SharedSessionRepository = Depends(get_shared_session_repository),
) -> SharedSessionDTO:
    session = await sessions.get_by_token(access_token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    updated = join_as_participant(session, participant_label=body.participant_label)
    saved = await sessions.update_session(updated)
    return _session_dto(saved)


@router.post("/shared-sessions/{access_token}/notes", response_model=SharedSessionWithNotesDTO)
async def add_shared_session_note(
    access_token: str,
    body: AddSharedSessionNoteRequest,
    sessions: SharedSessionRepository = Depends(get_shared_session_repository),
) -> SharedSessionWithNotesDTO:
    session = await sessions.get_by_token(access_token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    note = build_note(session.id, author_role=body.author_role, note=body.note)
    await sessions.add_note(note)
    notes = await sessions.list_notes(session.id)
    return SharedSessionWithNotesDTO(
        **_session_dto(session).model_dump(),
        notes=[
            SharedSessionNoteDTO(
                id=n.id, session_id=n.session_id, author_role=n.author_role, note=n.note,
                created_at=n.created_at,
            )
            for n in notes
        ],
    )


@student_router.post("/{student_id}/shared-sessions", response_model=SharedSessionDTO)
async def create_shared_session(
    student_id: str,
    body: CreateSharedSessionRequest,
    experts: ExpertRepository = Depends(get_expert_repository),
    sessions: SharedSessionRepository = Depends(get_shared_session_repository),
) -> SharedSessionDTO:
    mentor = await experts.get_expert(body.mentor_id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Expert not found")
    invite = create_invite(student_id=student_id, mentor=mentor, career_id=body.career_id, topic=body.topic)
    saved = await sessions.create_session(invite)
    return _session_dto(saved)


@student_router.get("/{student_id}/shared-sessions", response_model=SharedSessionsResponse)
async def list_shared_sessions(
    student_id: str,
    sessions: SharedSessionRepository = Depends(get_shared_session_repository),
) -> SharedSessionsResponse:
    results = await sessions.list_for_student(student_id)
    return SharedSessionsResponse(sessions=[_session_dto(s) for s in results])
