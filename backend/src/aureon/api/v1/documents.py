from fastapi import APIRouter, Depends, File, UploadFile

from aureon.agents.document_intelligence.pipeline import investigate_document
from aureon.agents.mission.snapshot import build_mission_snapshot, mission_snapshot_to_dto
from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    DocumentInvestigationRecordDTO,
    DocumentInvestigationResponse,
    DocumentInvestigationsResponse,
)

router = APIRouter(prefix="/students", tags=["document-intelligence"], dependencies=[Depends(require_own_profile)])


@router.post("/{student_id}/documents/analyze", response_model=DocumentInvestigationResponse)
async def analyze_document(
    student_id: str,
    file: UploadFile = File(...),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> DocumentInvestigationResponse:
    """Document Intelligence (V8) — classifies an uploaded document
    deterministically, routes it directly to the specialist that owns
    that document category, extracts real text (pypdf, no OCR), and
    folds the reasoned findings into the student's existing Evidence
    Graph/Discovery Notebook. Never fabricates content it couldn't
    actually read."""
    profile = await profiles.get_or_create(student_id)
    llm = get_llm_client()
    content = await file.read()

    result = await investigate_document(
        file.filename or "document.pdf", content, student_id=student_id, profile=profile, llm=llm,
    )

    if result.evidence_added:
        await profiles.save(profile)

    return DocumentInvestigationResponse(
        filename=result.filename,
        category=result.category,
        owning_specialist=result.owning_specialist,
        matched_on=result.matched_on,
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


@router.get("/{student_id}/document-investigations", response_model=DocumentInvestigationsResponse)
async def get_document_investigations(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> DocumentInvestigationsResponse:
    """Investigation History (V12) reopens one of these by id — a pure
    read of the already-persisted record, never a re-investigation."""
    profile = await profiles.get_or_create(student_id)
    return DocumentInvestigationsResponse(investigations=[
        DocumentInvestigationRecordDTO(
            id=r.id, filename=r.filename, category=r.category, owning_specialist=r.owning_specialist,
            title=r.title, summary=r.summary, key_findings=r.key_findings,
            structured_fields=r.structured_fields, created_at=r.created_at,
        )
        for r in profile.document_investigations
    ])
