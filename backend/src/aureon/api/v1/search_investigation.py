from fastapi import APIRouter, Depends

from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.agents.specialized.career_intelligence.search_investigation_pipeline import investigate_question
from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    CareerInvestigationRecordDTO,
    CareerInvestigationsResponse,
    FindingDTO,
    SearchInvestigationRequest,
    SearchInvestigationResponse,
    SourceAvailabilityDTO,
    SourceStatusDTO,
)

router = APIRouter(prefix="/students", tags=["search-investigation"], dependencies=[Depends(require_own_profile)])


@router.post("/{student_id}/search-investigations/analyze", response_model=SearchInvestigationResponse)
async def analyze_search_investigation(
    student_id: str,
    request: SearchInvestigationRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> SearchInvestigationResponse:
    """Career Intelligence's Multi-Source Search Intelligence (V10) —
    investigates a real career question across Wikipedia, arXiv, and
    Semantic Scholar, cross-verifies the real evidence collected, and
    folds it into the student's existing Evidence Graph/Discovery
    Notebook/Career Investigations. Never answers from LLM memory alone."""
    profile = await profiles.get_or_create(student_id)
    llm = get_llm_client()

    result = await investigate_question(request.question, student_id=student_id, profile=profile, llm=llm)

    if result.evidence_added:
        await profiles.save(profile)

    source_availability = (
        SourceAvailabilityDTO(
            total_sources=result.source_availability.total_sources,
            sources_retrieved=result.source_availability.sources_retrieved,
            sources_unavailable=result.source_availability.sources_unavailable,
            sources=[
                SourceStatusDTO(name=s.name, category=s.category, reached=s.reached, note=s.note)
                for s in result.source_availability.sources
            ],
        )
        if result.source_availability
        else None
    )

    return SearchInvestigationResponse(
        question=result.question,
        status=result.status.value,
        overall_summary=result.overall_summary,
        findings=[
            FindingDTO(claim=f.claim, status=f.status, citing_sources=f.citing_sources, explanation=f.explanation)
            for f in result.findings
        ],
        agreements=result.agreements,
        disagreements=result.disagreements,
        related_career_id=result.related_career_id,
        source_availability=source_availability,
        explanation=result.explanation,
        stages=result.stages,
        evidence_added=result.evidence_added,
        mission=mission_snapshot_to_dto(build_mission_snapshot(result.mission)),
        artifacts_updated=result.artifacts_updated,
    )


@router.get("/{student_id}/search-investigations", response_model=CareerInvestigationsResponse)
async def get_search_investigations(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerInvestigationsResponse:
    """Investigation History (V12) reopens one of these by id — a pure
    read of the already-persisted record, never a re-investigation."""
    profile = await profiles.get_or_create(student_id)
    return CareerInvestigationsResponse(investigations=[
        CareerInvestigationRecordDTO(
            id=inv.id, question=inv.question, overall_summary=inv.overall_summary,
            findings=[
                FindingDTO(claim=f.claim, status=f.status, citing_sources=f.citing_sources, explanation=f.explanation)
                for f in inv.findings
            ],
            related_career_id=inv.related_career_id, created_at=inv.created_at,
        )
        for inv in profile.career_investigations
    ])
