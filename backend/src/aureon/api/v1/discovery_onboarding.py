from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from aureon.api.deps import get_experiment_repository, get_student_profile_repository, require_own_profile
from aureon.core.config import Settings, get_settings
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.discovery_onboarding import complete_onboarding
from aureon.domain.services.progressive_discovery import get_progressive_discovery_state
from aureon.domain.services.world_signal import answer_world_followup
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CuriosityCheckInAnswerRequest,
    OnboardingRequest,
    ProgressiveDiscoveryStateResponse,
)

router = APIRouter(prefix="/students", tags=["discovery-onboarding"], dependencies=[Depends(require_own_profile)])


def _mode_for(profile: StudentProfile, settings: Settings) -> str:
    """Same inline computation as api/v1/students.py's discovery-profile
    route — no stored `mode` field, no new shared helper for 3 call
    sites, matches existing precedent exactly."""
    return "recommendation" if profile.confidence_score >= settings.min_recommendation_confidence else "exploration"


@router.post("/{student_id}/onboarding", response_model=ProgressiveDiscoveryStateResponse)
async def submit_onboarding(
    student_id: str,
    body: OnboardingRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    settings: Settings = Depends(get_settings),
) -> ProgressiveDiscoveryStateResponse:
    """Real, persisted onboarding submission — Profile Service's write
    path. Thin route: no business logic, just a repository read/write
    plus domain/services/discovery_onboarding.py."""
    profile = await profiles.get_or_create(student_id)
    complete_onboarding(
        profile,
        name=body.name, age=body.age, stage=body.stage,
        location_state=body.location_state, location_city=body.location_city,
        preferred_language=body.preferred_language, current_situation=body.current_situation,
        worlds=body.worlds, worlds_unsure=body.worlds_unsure,
        now=datetime.now(timezone.utc),
    )
    await profiles.save(profile)
    return get_progressive_discovery_state(profile, mode=_mode_for(profile, settings))


@router.get("/{student_id}/progressive-discovery", response_model=ProgressiveDiscoveryStateResponse)
async def get_progressive_discovery(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    experiments: ExperimentRepository = Depends(get_experiment_repository),
    settings: Settings = Depends(get_settings),
) -> ProgressiveDiscoveryStateResponse:
    """Lets the frontend restore Orbit Status + the one pending Curiosity
    Check-in for a returning student — same read-only, no-business-logic
    shape as GET .../discovery-profile. Discover Batch 2 — the only call
    site that also passes the Experiment catalog, so this response's
    ``suggested_experiment`` is real here."""
    profile = await profiles.get_or_create(student_id)
    catalog = await experiments.list_experiments()
    return get_progressive_discovery_state(profile, mode=_mode_for(profile, settings), experiments=catalog)


@router.post("/{student_id}/curiosity-checkins/answer", response_model=ProgressiveDiscoveryStateResponse)
async def answer_curiosity_checkin(
    student_id: str,
    body: CuriosityCheckInAnswerRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    settings: Settings = Depends(get_settings),
) -> ProgressiveDiscoveryStateResponse:
    """Records a real Curiosity Check-in answer and returns the fresh
    state so the frontend knows the next pending world without a second
    round trip."""
    profile = await profiles.get_or_create(student_id)
    answer_world_followup(
        profile, world=body.world, chosen_options=body.chosen_options, now=datetime.now(timezone.utc)
    )
    await profiles.save(profile)
    return get_progressive_discovery_state(profile, mode=_mode_for(profile, settings))
