import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from starlette.concurrency import run_in_threadpool

from aureon.core.config import Settings, get_settings
from aureon.domain.services.conversation_service import ConversationService
from aureon.services.supabase.client import get_supabase_client
from aureon.services.supabase.repositories.career_event_repository import CareerEventRepository
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.career_world_repository import CareerWorldRepository
from aureon.services.supabase.repositories.conversation_repository import (
    ConversationRepository,
)
from aureon.services.supabase.repositories.entrance_exam_repository import EntranceExamRepository
from aureon.services.supabase.repositories.expert_repository import ExpertRepository
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.journey_story_repository import JourneyStoryRepository
from aureon.services.supabase.repositories.knowledge_circle_repository import KnowledgeCircleRepository
from aureon.services.supabase.repositories.learning_style_repository import LearningStyleRepository
from aureon.services.supabase.repositories.life_mission_repository import LifeMissionRepository
from aureon.services.supabase.repositories.mentor_repository import MentorRepository
from aureon.services.supabase.repositories.mentorship_repository import MentorshipRepository
from aureon.services.supabase.repositories.parent_connect_repository import ParentConnectRepository
from aureon.services.supabase.repositories.shared_session_repository import SharedSessionRepository
from aureon.services.supabase.repositories.suggestion_repository import SuggestionRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.services.supabase.repositories.company_repository import CompanyRepository
from aureon.services.supabase.repositories.project_repository import ProjectRepository
from aureon.services.supabase.repositories.skill_repository import SkillRepository
from aureon.services.supabase.repositories.topic_resource_repository import TopicResourceRepository
from aureon.services.supabase.repositories.trend_repository import TrendRepository

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_conversation_repository() -> ConversationRepository:
    return ConversationRepository()


def get_student_profile_repository() -> StudentProfileRepository:
    return StudentProfileRepository()


def get_career_repository() -> CareerRepository:
    return CareerRepository()


def get_skill_repository() -> SkillRepository:
    return SkillRepository()


def get_company_repository() -> CompanyRepository:
    return CompanyRepository()


def get_project_repository() -> ProjectRepository:
    return ProjectRepository()


def get_mentor_repository() -> MentorRepository:
    return MentorRepository()


def get_expert_repository() -> ExpertRepository:
    return ExpertRepository()


def get_parent_connect_repository() -> ParentConnectRepository:
    return ParentConnectRepository()


def get_shared_session_repository() -> SharedSessionRepository:
    return SharedSessionRepository()


def get_journey_story_repository() -> JourneyStoryRepository:
    return JourneyStoryRepository()


def get_knowledge_circle_repository() -> KnowledgeCircleRepository:
    return KnowledgeCircleRepository()


def get_mentorship_repository() -> MentorshipRepository:
    return MentorshipRepository()


def get_institution_repository() -> InstitutionRepository:
    return InstitutionRepository()


def get_career_event_repository() -> CareerEventRepository:
    return CareerEventRepository()


def get_trend_repository() -> TrendRepository:
    return TrendRepository()


def get_entrance_exam_repository() -> EntranceExamRepository:
    return EntranceExamRepository()


def get_experiment_repository() -> ExperimentRepository:
    return ExperimentRepository()


def get_career_world_repository() -> CareerWorldRepository:
    return CareerWorldRepository()


def get_life_mission_repository() -> LifeMissionRepository:
    return LifeMissionRepository()


def get_learning_style_repository() -> LearningStyleRepository:
    return LearningStyleRepository()


def get_topic_resource_repository() -> TopicResourceRepository:
    return TopicResourceRepository()


def get_suggestion_repository() -> SuggestionRepository:
    return SuggestionRepository()


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


async def require_reviewer_secret(
    settings: SettingsDep,
    x_aureon_reviewer_secret: Annotated[str | None, Header()] = None,
) -> None:
    """Gates the reviewer-facing suggestion endpoints
    (``api/v1/suggestions.py``). There is no admin/staff role anywhere in
    this system — a valid student session grants zero access here, only
    possessing this secret does. If the secret isn't configured, the
    endpoints fail closed rather than being silently open."""
    configured = settings.suggestion_reviewer_secret
    if not configured or not x_aureon_reviewer_secret or not secrets.compare_digest(
        x_aureon_reviewer_secret, configured
    ):
        raise HTTPException(status_code=403, detail="Missing or invalid reviewer secret.")
