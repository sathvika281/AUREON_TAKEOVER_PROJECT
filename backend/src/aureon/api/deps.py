from typing import Annotated

from fastapi import Depends, Header, HTTPException
from starlette.concurrency import run_in_threadpool

from aureon.core.config import Settings, get_settings
from aureon.domain.services.conversation_service import ConversationService
from aureon.services.supabase.client import get_supabase_client
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.conversation_repository import (
    ConversationRepository,
)
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_conversation_repository() -> ConversationRepository:
    return ConversationRepository()


def get_student_profile_repository() -> StudentProfileRepository:
    return StudentProfileRepository()


def get_career_repository() -> CareerRepository:
    return CareerRepository()


def get_mentor_repository() -> MentorRepository:
    return MentorRepository()


def get_institution_repository() -> InstitutionRepository:
    return InstitutionRepository()


def get_career_event_repository() -> CareerEventRepository:
    return CareerEventRepository()


def get_conversation_service(
    conversations: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    profiles: Annotated[StudentProfileRepository, Depends(get_student_profile_repository)],
) -> ConversationService:
    return ConversationService(conversations, profiles)


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]


async def get_current_user_id(authorization: str | None = Header(None)) -> str:
    """V12 — real Supabase Auth verification. A network-verified check
    (``auth.get_user``) against Supabase's own Auth server, deliberately
    not local JWT decoding — the simplest correct approach, matching
    "keep authentication intentionally simple"."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")
    token = authorization.split(" ", 1)[1].strip()

    def _verify() -> str | None:
        try:
            response = get_supabase_client().auth.get_user(token)
        except Exception:  # noqa: BLE001 — any verification failure is just "not authenticated"
            return None
        return response.user.id if response and response.user else None

    user_id = await run_in_threadpool(_verify)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return user_id


async def require_own_profile(
    student_id: str, user_id: Annotated[str, Depends(get_current_user_id)]
) -> str:
    """Applied at the router level (``APIRouter(dependencies=[...])``) on
    every ``/students/{student_id}/...`` router — FastAPI resolves
    ``student_id`` from the request's real path params regardless of
    where the dependency is declared, so this protects every route in
    that file without touching any individual route function. Never
    exposes another student's profile: the path's ``student_id`` must
    exactly match the verified, authenticated user's own id."""
    if user_id != student_id:
        raise HTTPException(status_code=403, detail="You can only access your own profile.")
    return student_id
