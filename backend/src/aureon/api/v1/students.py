from fastapi import APIRouter, Depends

from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.core.config import Settings, get_settings
from aureon.domain.services.profile_view import (
    build_career_dna_dto,
    build_evidence_graph_dtos,
    build_hidden_potential_dtos,
    build_hypothesis_dtos,
    build_notebook_entry_dtos,
    build_understanding_level,
)
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import DiscoveryProfileResponse, ReflectionEntryDTO

router = APIRouter(prefix="/students", tags=["students"], dependencies=[Depends(require_own_profile)])


@router.get("/{student_id}/discovery-profile", response_model=DiscoveryProfileResponse)
async def get_discovery_profile(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    settings: Settings = Depends(get_settings),
) -> DiscoveryProfileResponse:
    """Lets the frontend restore the Discovery Notebook for a returning
    student — the persisted Career DNA, hypotheses, Evidence Graph, and
    Notebook — without replaying the conversation or recomputing anything
    client-side. Thin route: no business logic, just a repository read
    plus the shared DTO mapping in ``domain/services/profile_view.py``.
    """
    profile = await profiles.get_or_create(student_id)
    mode = (
        "recommendation"
        if profile.confidence_score >= settings.min_recommendation_confidence
        else "exploration"
    )
    understanding_stage, understanding_narrative = build_understanding_level(profile, mode=mode)

    return DiscoveryProfileResponse(
        student_id=profile.student_id,
        confidence_score=profile.confidence_score,
        understanding_stage=understanding_stage,
        understanding_narrative=understanding_narrative,
        career_dna=build_career_dna_dto(profile),
        hypotheses=build_hypothesis_dtos(profile),
        hidden_potential=build_hidden_potential_dtos(profile),
        notebook_entries=build_notebook_entry_dtos(profile),
        evidence_graph=build_evidence_graph_dtos(profile),
        reflection_journal=[
            ReflectionEntryDTO(
                prompt=r.prompt,
                response=r.response,
                created_at=r.created_at,
                answered_at=r.answered_at,
            )
            for r in profile.reflection_journal
        ],
    )
