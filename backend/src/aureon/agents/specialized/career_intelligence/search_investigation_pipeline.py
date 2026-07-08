import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.mission.mission import Mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.specialized.career_intelligence.cross_verification import analyze_evidence
from aureon.agents.specialized.career_intelligence.investigation_planning import plan_investigation
from aureon.agents.specialized.career_intelligence.search_sources import SourceAvailability, build_source_availability
from aureon.agents.specialized.career_intelligence.tools import MultiSourceSearchTool
from aureon.agents.tools.base import ToolStatus, run_tool_safely
from aureon.domain.models.career_investigation import CareerInvestigationRecord, InvestigationFinding
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName

#: Observable execution stages for Multi-Source Search Intelligence — a
#: pipeline, not a single specialist call, same reasoning as
#: URL_INVESTIGATION_STAGES.
SEARCH_INVESTIGATION_STAGES = [
    "Mission Created",
    "Planning Investigation",
    "Searching Sources",
    "Extracting Evidence",
    "Cross-Verifying",
    "Knowledge Fusion",
    "Updating Reports",
    "Investigation Complete",
]

#: How many of the student's own previous investigations to preload as
#: Memory Recall context — a small, bounded window, not the full history.
_PRIOR_INVESTIGATIONS_WINDOW = 3


class SearchInvestigationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    question: str
    status: ToolStatus
    overall_summary: str | None = None
    findings: list[InvestigationFinding] = Field(default_factory=list)
    agreements: list[str] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    related_career_id: str | None = None
    source_availability: SourceAvailability | None = None
    explanation: str | None = None
    stages: list[str] = Field(default_factory=list)
    evidence_added: bool = False
    #: V7 — Mission Workspace reads this via
    #: agents/mission/snapshot.py::build_mission_snapshot(...) at the
    #: route layer; this pipeline never builds the snapshot/DTO itself.
    mission: Mission
    artifacts_updated: list[str] = Field(default_factory=list)


def _known_candidates(profile: StudentProfile) -> list[tuple[str, str]]:
    return [
        (c.career_id, c.career_name)
        for c in profile.career_candidates
        if c.status == "active"
    ]


async def investigate_question(
    question: str, *, student_id: str, profile: StudentProfile, llm: LLMClient
) -> SearchInvestigationResult:
    """Career Intelligence's Multi-Source Search Intelligence pipeline
    (V10) — reuses the Mission Orchestrator, Tool Architecture, and
    Knowledge Fusion exactly as V4/V5 built them; no delegation, since
    Career Intelligence already owns INVESTIGATION/PLANNING/
    KNOWLEDGE_FUSION/TREND_MONITORING outright."""
    prior = [
        {"question": inv.question, "overall_summary": inv.overall_summary}
        for inv in profile.career_investigations[-_PRIOR_INVESTIGATIONS_WINDOW:]
    ]
    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective="search_investigation", primary_agent=AgentName.CAREER_INTELLIGENCE.value,
        prior_artifacts={"previous_investigations": prior} if prior else None,
    )
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[0])  # "Mission Created"
    MissionOrchestrator.begin_execution(mission)

    known_candidates = _known_candidates(profile)
    plan = await plan_investigation(
        question, known_candidates=[name for _, name in known_candidates], llm=llm,
    )
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[1])  # "Planning Investigation"

    search_tool = MultiSourceSearchTool()
    tool_result = await run_tool_safely(
        search_tool,
        wikipedia_query=plan.wikipedia_query,
        arxiv_query=plan.arxiv_query,
        semantic_scholar_query=plan.semantic_scholar_query,
    )
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[2])  # "Searching Sources"
    mission.artifacts.setdefault("tool_results", {})[AgentName.CAREER_INTELLIGENCE.value] = [
        tool_result.model_dump()
    ]

    source_availability = (
        build_source_availability(search_tool.last_outcomes) if search_tool.last_outcomes else None
    )

    if tool_result.status != ToolStatus.COMPLETED:
        MissionOrchestrator.complete(mission)
        return SearchInvestigationResult(
            question=question, status=tool_result.status, explanation=tool_result.explanation,
            source_availability=source_availability, stages=mission.stage_log, mission=mission,
        )
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[3])  # "Extracting Evidence"

    output = await analyze_evidence(
        question, tool_result.evidence, known_candidates=known_candidates, llm=llm,
    )
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[4])  # "Cross-Verifying"

    MissionOrchestrator.fuse_knowledge(mission, {
        "search_evidence": [e.model_dump() for e in tool_result.evidence],
        "findings": [f.model_dump() for f in output.findings],
    })
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[5])  # "Knowledge Fusion"

    evidence_added = False
    artifacts_updated: list[str] = []
    if not output.insufficient_evidence:
        now = datetime.now(timezone.utc)
        for finding in output.findings:
            # A finding genuinely marked "insufficient_evidence" isn't
            # itself evidence for or against anything — recording it under
            # EvidenceRecord's binary supports/contradicts relation would
            # misrepresent a real gap as a real signal.
            if finding.status == "insufficient_evidence":
                continue
            profile.evidence_graph.append(
                EvidenceRecord(
                    id=str(uuid.uuid4()), text=finding.explanation, source="search",
                    related_career=output.related_career_id,
                    relation="contradicts" if finding.status == "contradicted" else "supports",
                    created_at=now,
                )
            )
        profile.notebook_entries.append(
            NotebookEntry(
                id=str(uuid.uuid4()), kind="observation", text=output.overall_summary,
                source="search", related_career=output.related_career_id, created_at=now,
            )
        )
        profile.career_investigations.append(
            CareerInvestigationRecord(
                id=str(uuid.uuid4()), question=question, overall_summary=output.overall_summary,
                findings=output.findings, related_career_id=output.related_career_id, created_at=now,
            )
        )
        evidence_added = True
        artifacts_updated = ["Evidence Graph Updated", "Discovery Notebook Updated", "Career Investigations Updated"]
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[6])  # "Updating Reports"

    MissionOrchestrator.complete(mission)
    mission.record_stage(SEARCH_INVESTIGATION_STAGES[7])  # "Investigation Complete"

    return SearchInvestigationResult(
        question=question, status=tool_result.status, overall_summary=output.overall_summary,
        findings=output.findings, agreements=output.agreements, disagreements=output.disagreements,
        related_career_id=output.related_career_id, source_availability=source_availability,
        explanation=output.insufficient_evidence_reason, stages=mission.stage_log,
        evidence_added=evidence_added, mission=mission, artifacts_updated=artifacts_updated,
    )
