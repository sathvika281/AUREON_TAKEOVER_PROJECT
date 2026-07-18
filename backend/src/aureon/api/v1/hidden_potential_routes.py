from fastapi import APIRouter, Depends

from aureon.api.deps import get_experiment_repository, get_student_profile_repository, require_own_profile
from aureon.domain.services.hidden_potential import build_hidden_potential_response
from aureon.services.supabase.repositories.experiment_repository import ExperimentRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import HiddenPotentialResponse

router = APIRouter(prefix="/students", tags=["hidden-potential"], dependencies=[Depends(require_own_profile)])


@router.get("/{student_id}/hidden-potential", response_model=HiddenPotentialResponse)
async def get_hidden_potential(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    experiments: ExperimentRepository = Depends(get_experiment_repository),
) -> HiddenPotentialResponse:
    """The single canonical source for strengths/potential/evidence
    progression — composes the existing Hidden Potential Engine, Talent
    Pattern Engine, Experiment History, and Progressive Discovery's
    suggested-experiment recommendation. Nothing here is recomputed; see
    domain/services/hidden_potential.py."""
    profile = await profiles.get_or_create(student_id)
    catalog = await experiments.list_experiments()
    return build_hidden_potential_response(profile, experiments=catalog)
