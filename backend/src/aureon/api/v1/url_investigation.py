from fastapi import APIRouter, Depends

from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.specialized.career_intelligence.url_investigation_pipeline import investigate_url
from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import UrlInvestigationRequest, UrlInvestigationResponse

router = APIRouter(prefix="/students", tags=["url-investigation"], dependencies=[Depends(require_own_profile)])


@router.post("/{student_id}/url-investigations/analyze", response_model=UrlInvestigationResponse)
async def analyze_url_investigation(
    student_id: str,
    request: UrlInvestigationRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> UrlInvestigationResponse:
    """Career Intelligence's URL Intelligence (V6) — fetches a real URL,
    classifies it deterministically, delegates to the owning specialist
    when appropriate, and folds real extracted evidence into the
    student's existing Evidence Graph/Discovery Notebook. Never fetches
    or fabricates anything when the URL can't actually be read."""
    profile = await profiles.get_or_create(student_id)
    llm = get_llm_client()

    result = await investigate_url(request.url, student_id=student_id, profile=profile, llm=llm)

    if result.evidence_added:
        await profiles.save(profile)

    return UrlInvestigationResponse(
        url=result.url,
        category=result.category,
        owning_specialist=result.owning_specialist,
        delegated=result.delegated,
        status=result.status.value,
        title=result.title,
        summary=result.summary,
        key_findings=result.key_findings,
        structured_fields=result.structured_fields,
        explanation=result.explanation,
        stages=result.stages,
        evidence_added=result.evidence_added,
        mission=mission_snapshot_to_dto(build_mission_snapshot(result.mission)),
        artifacts_updated=result.artifacts_updated,
    )
