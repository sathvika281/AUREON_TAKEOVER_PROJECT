import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.agents.mission.capabilities import Capability
from aureon.agents.mission.mission import Mission
from aureon.agents.mission.orchestrator import MissionOrchestrator
from aureon.agents.specialized.career_intelligence.tools import URLReaderTool
from aureon.agents.specialized.career_intelligence.url_classifier import (
    URL_CATEGORY_OWNER,
    UrlCategory,
    classify_url,
)
from aureon.agents.specialized.career_intelligence.url_investigation import (
    analyze_url_content,
    finalize_url_evidence,
)
from aureon.agents.tools.base import ToolStatus, run_tool_safely
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient
from aureon.shared.types import AgentName

#: Observable execution stages for URL Intelligence — a pipeline, not a
#: single specialist, so this lives alongside the pipeline rather than
#: inside agents/mission/stages.py's per-agent dict.
URL_INVESTIGATION_STAGES = [
    "Mission Started",
    "Planning Investigation",
    "Fetching URL",
    "Reading Content",
    "Extracting Evidence",
    "Cross-Verifying",
    "Knowledge Fusion",
    "Updating Reports",
    "Investigation Complete",
]


class UrlInvestigationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    url: str
    category: UrlCategory
    owning_specialist: str
    delegated: bool
    status: ToolStatus
    title: str | None = None
    summary: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    structured_fields: dict[str, str] = Field(default_factory=dict)
    explanation: str | None = None
    stages: list[str] = Field(default_factory=list)
    evidence_added: bool = False
    #: V7 — Mission Workspace reads this via
    #: agents/mission/snapshot.py::build_mission_snapshot(...) at the
    #: route layer; this pipeline never builds the snapshot/DTO itself.
    mission: Mission
    artifacts_updated: list[str] = Field(default_factory=list)


async def investigate_url(
    url: str, *, student_id: str, profile: StudentProfile, llm: LLMClient
) -> UrlInvestigationResult:
    """Career Intelligence's URL Intelligence pipeline (V6) — reuses the
    Mission Orchestrator, delegation, and capability ownership exactly as
    V4/V5 built them; adds nothing new to any of them."""
    category = classify_url(url)
    owner = URL_CATEGORY_OWNER[category]

    mission = MissionOrchestrator.create_mission(
        student_id=student_id, objective=f"url_investigation:{category}", primary_agent=AgentName.CAREER_INTELLIGENCE.value,
    )
    mission.record_stage(URL_INVESTIGATION_STAGES[0])  # "Mission Started"
    MissionOrchestrator.begin_execution(mission)
    mission.record_stage(URL_INVESTIGATION_STAGES[1])  # "Planning Investigation"

    fetch_result = await run_tool_safely(URLReaderTool(), url=url)
    mission.record_stage(URL_INVESTIGATION_STAGES[2])  # "Fetching URL"
    mission.artifacts.setdefault("tool_results", {})[AgentName.CAREER_INTELLIGENCE.value] = [
        fetch_result.model_dump()
    ]

    if fetch_result.status != ToolStatus.COMPLETED:
        MissionOrchestrator.complete(mission)
        return UrlInvestigationResult(
            url=url, category=category, owning_specialist=owner, delegated=False,
            status=fetch_result.status, explanation=fetch_result.explanation,
            stages=mission.stage_log, mission=mission,
        )

    raw_text = fetch_result.evidence[0].summary
    mission.record_stage(URL_INVESTIGATION_STAGES[3])  # "Reading Content"

    delegated = owner != AgentName.CAREER_INTELLIGENCE.value

    async def _analyze():
        return await analyze_url_content(category=category, raw_text=raw_text, url=url, llm=llm)

    if delegated:
        output = await MissionOrchestrator.delegate(
            mission,
            from_agent=AgentName.CAREER_INTELLIGENCE.value,
            to_agent=owner,
            capability=Capability.INVESTIGATION,
            reason=f"'{category}' pages belong to {owner}'s expertise, not Career Intelligence's.",
            call=_analyze,
        )
    else:
        output = await _analyze()
    mission.record_stage(URL_INVESTIGATION_STAGES[4])  # "Extracting Evidence"
    mission.record_stage(URL_INVESTIGATION_STAGES[5])  # "Cross-Verifying"

    evidence = finalize_url_evidence(category=category, url=url, raw_text=raw_text, output=output)
    MissionOrchestrator.fuse_knowledge(mission, {"url_evidence": evidence.model_dump()})
    mission.record_stage(URL_INVESTIGATION_STAGES[6])  # "Knowledge Fusion"

    evidence_added = False
    artifacts_updated: list[str] = []
    if not output.insufficient_content:
        now = datetime.now(timezone.utc)
        profile.evidence_graph.append(
            EvidenceRecord(
                id=str(uuid.uuid4()), text=evidence.summary, source="url",
                relation="supports", created_at=now,
            )
        )
        profile.notebook_entries.append(
            NotebookEntry(
                id=str(uuid.uuid4()), kind="observation", text=evidence.summary,
                source=f"url:{category}", created_at=now,
            )
        )
        evidence_added = True
        artifacts_updated = ["Evidence Graph Updated", "Discovery Notebook Updated"]
    mission.record_stage(URL_INVESTIGATION_STAGES[7])  # "Updating Reports"

    MissionOrchestrator.complete(mission)
    mission.record_stage(URL_INVESTIGATION_STAGES[8])  # "Investigation Complete"

    return UrlInvestigationResult(
        url=url, category=category, owning_specialist=owner, delegated=delegated,
        status=fetch_result.status, title=output.title, summary=output.summary,
        key_findings=output.key_findings, structured_fields=output.structured_fields,
        explanation=output.insufficient_content_reason, stages=mission.stage_log,
        evidence_added=evidence_added, mission=mission, artifacts_updated=artifacts_updated,
    )
