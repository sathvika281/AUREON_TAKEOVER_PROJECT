import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.document_intelligence.classifier import (
    DOCUMENT_CATEGORY_OWNER,
    DocumentCategory,
    classify_document,
)
from aureon.agents.document_intelligence.reasoning import analyze_document_content, finalize_document_evidence
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.specialized.career_intelligence.tools import ResearchPaperReaderTool
from aureon.agents.specialized.discovery.tools import PDFReaderTool, ResumeReaderTool
from aureon.agents.specialized.institution.tools import AdmissionPDFReaderTool, CurriculumReaderTool
from aureon.agents.specialized.mentor.tools import PublicationReaderTool
from aureon.agents.tools.base import Tool, ToolStatus, run_tool_safely
from aureon.agents.tools.pdf_extraction import extract_pdf_text
from aureon.domain.models.document_investigation import DocumentInvestigationRecord
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient

#: Observable execution stages for Document Intelligence — a pipeline,
#: not a single specialist (no one agent owns Document Intelligence
#: overall, unlike Career Intelligence owning URL Intelligence in V6), so
#: this lives alongside the pipeline rather than inside
#: agents/mission/stages.py's per-agent dict.
DOCUMENT_INVESTIGATION_STAGES = [
    "Mission Started",
    "Classifying Document",
    "Reading Document",
    "Extracting Evidence",
    "Knowledge Fusion",
    "Updating Reports",
    "Investigation Complete",
]

#: Which specialist's real Tool actually performs the extraction for a
#: given category — every category maps to exactly one owner (see
#: DOCUMENT_CATEGORY_OWNER) and exactly one tool here.
_CATEGORY_TOOL: dict[DocumentCategory, type[Tool]] = {
    "resume": ResumeReaderTool,
    "cv": ResumeReaderTool,
    "portfolio": PDFReaderTool,
    "certificate": PDFReaderTool,
    "transcript": PDFReaderTool,
    "sop": PDFReaderTool,
    "university_brochure": CurriculumReaderTool,
    "admission_document": AdmissionPDFReaderTool,
    "curriculum": CurriculumReaderTool,
    "research_paper": ResearchPaperReaderTool,
    "whitepaper": ResearchPaperReaderTool,
    "industry_report": ResearchPaperReaderTool,
    "faculty_profile": PublicationReaderTool,
    "publication": PublicationReaderTool,
}


class DocumentInvestigationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    filename: str
    category: DocumentCategory
    owning_specialist: str
    matched_on: str
    status: ToolStatus
    title: str | None = None
    summary: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    structured_fields: dict[str, str] = Field(default_factory=dict)
    explanation: str | None = None
    stages: list[str] = Field(default_factory=list)
    evidence_added: bool = False
    #: Read by the route via agents/mission/snapshot.py::build_mission_snapshot
    #: — this pipeline never builds the DTO itself.
    mission: Mission
    artifacts_updated: list[str] = Field(default_factory=list)


async def investigate_document(
    filename: str, content: bytes, *, student_id: str, profile: StudentProfile, llm: LLMClient
) -> DocumentInvestigationResult:
    """Document Intelligence's pipeline (V8). Unlike URL Intelligence
    (V6), no single specialist owns Document Intelligence overall — every
    category maps directly to one true owner (see
    document_intelligence/classifier.py), so Mission.primary_agent is set
    directly to that owner and MissionOrchestrator.delegate() is never
    called in this flow."""
    # Classification may need real first-page text for generic filenames
    # (document.pdf, file.pdf, ...) — this pre-extraction is the same
    # shared, specialist-agnostic function every tool below also calls;
    # it's used here only to make classification possible, not persisted
    # or treated as evidence itself.
    pre_extraction = extract_pdf_text(content)
    first_page_text = pre_extraction.first_page_text if pre_extraction.status == "completed" else None
    classification = classify_document(filename, first_page_text)
    category = classification.category
    owner = classification.owning_specialist

    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective=f"document_investigation:{category}", primary_agent=owner,
    )
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[0])  # "Mission Started"
    MissionOrchestrator.begin_execution(mission)
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[1])  # "Classifying Document"

    tool_cls = _CATEGORY_TOOL[category]
    tool_result = await run_tool_safely(tool_cls(), content=content, filename=filename)
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[2])  # "Reading Document"
    mission.artifacts.setdefault("tool_results", {})[owner] = [tool_result.model_dump()]

    if tool_result.status != ToolStatus.COMPLETED:
        MissionOrchestrator.complete(mission)
        return DocumentInvestigationResult(
            filename=filename, category=category, owning_specialist=owner, matched_on=classification.matched_on,
            status=tool_result.status, explanation=tool_result.explanation, stages=mission.stage_log,
            mission=mission,
        )

    raw_text = tool_result.evidence[0].summary
    output = await analyze_document_content(category=category, filename=filename, raw_text=raw_text, llm=llm)
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[3])  # "Extracting Evidence"

    evidence = finalize_document_evidence(
        category=category, filename=filename, raw_text_length=len(raw_text), output=output,
    )
    MissionOrchestrator.fuse_knowledge(mission, {"document_evidence": evidence.model_dump()})
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[4])  # "Knowledge Fusion"

    evidence_added = False
    artifacts_updated: list[str] = []
    if not output.insufficient_content:
        now = datetime.now(timezone.utc)
        # Evidence.summary here is the reasoned, concise finding — never
        # the raw multi-page extracted text, which is discarded once
        # analyze_document_content() has already turned it into this.
        profile.evidence_graph.append(
            EvidenceRecord(
                id=str(uuid.uuid4()), text=evidence.summary, source="document",
                relation="supports", created_at=now,
            )
        )
        profile.notebook_entries.append(
            NotebookEntry(
                id=str(uuid.uuid4()), kind="observation", text=evidence.summary,
                source=f"document:{category}", created_at=now,
            )
        )
        evidence_added = True
        artifacts_updated = ["Evidence Graph Updated", "Discovery Notebook Updated"]

        # V12 — Investigation History needs a genuinely reopenable record,
        # which Document Intelligence never persisted before; additive
        # only, no change to the reasoning/evidence above.
        profile.document_investigations.append(
            DocumentInvestigationRecord(
                id=str(uuid.uuid4()), filename=filename, category=category, owning_specialist=owner,
                title=output.title, summary=output.summary, key_findings=output.key_findings,
                structured_fields=output.structured_fields, created_at=now,
            )
        )
        artifacts_updated.append("Investigation History Updated")
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[5])  # "Updating Reports"

    MissionOrchestrator.complete(mission)
    mission.record_stage(DOCUMENT_INVESTIGATION_STAGES[6])  # "Investigation Complete"

    return DocumentInvestigationResult(
        filename=filename, category=category, owning_specialist=owner, matched_on=classification.matched_on,
        status=tool_result.status, title=output.title, summary=output.summary,
        key_findings=output.key_findings, structured_fields=output.structured_fields,
        explanation=output.insufficient_content_reason, stages=mission.stage_log,
        evidence_added=evidence_added, mission=mission, artifacts_updated=artifacts_updated,
    )
