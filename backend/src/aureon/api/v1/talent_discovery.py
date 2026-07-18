from fastapi import APIRouter, Depends

from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.domain.services.talent_pattern_engine import analyze_talents
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import TalentEvidenceItemDTO, TalentPatternDTO, TalentsResponse

router = APIRouter(prefix="/students", tags=["talent-discovery"], dependencies=[Depends(require_own_profile)])


@router.get("/{student_id}/talents", response_model=TalentsResponse)
async def get_talents(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> TalentsResponse:
    """Continuously re-derived from real evidence — Career DNA, Career
    Experiments, Reflection Journal — never a stored score. Every
    pattern carries its own real, evidence-citing explanation."""
    profile = await profiles.get_or_create(student_id)
    patterns = analyze_talents(profile)
    return TalentsResponse(
        patterns=[
            TalentPatternDTO(
                talent=p.talent,
                tier=p.tier,
                explanation=p.explanation,
                evidence=[
                    TalentEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
                    for e in p.evidence
                ],
            )
            for p in patterns
        ]
    )
