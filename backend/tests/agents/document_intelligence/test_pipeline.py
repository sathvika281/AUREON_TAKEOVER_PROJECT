from aureon.agents.document_intelligence.pipeline import investigate_document
from aureon.agents.mission.mission import MissionStatus
from aureon.agents.mission.snapshot import build_mission_snapshot
from aureon.agents.specialized.discovery.tools import PDFReaderTool, ResumeReaderTool
from aureon.agents.tools.base import Evidence, ToolResult, ToolStatus
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import AgentName
from tests.fakes import FakeLLMClient, tool_call_response

INVESTIGATION_ARGS = {
    "title": "Resume Findings",
    "summary": "A concise, reasoned summary of the resume.",
    "key_findings": ["Strong Python background"],
    "structured_fields": {"skills": "Python, SQL"},
    "insufficient_content": False,
}


async def test_successful_resume_investigation_appends_concise_evidence_not_raw_text(monkeypatch):
    raw_text = "EDUCATION EXPERIENCE SKILLS PROJECTS " * 20  # long real extracted text

    async def fake_execute(self, *, content, filename="resume.pdf", **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=filename, summary=raw_text)],
        )

    monkeypatch.setattr(ResumeReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_document_investigation", INVESTIGATION_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_document(
        "resume.pdf", b"irrelevant-bytes-since-tool-is-mocked",
        student_id="s1", profile=profile, llm=llm,
    )

    assert result.category == "resume"
    assert result.owning_specialist == AgentName.DISCOVERY.value
    assert result.evidence_added is True
    assert len(profile.evidence_graph) == 1
    # Evidence stored is the reasoned summary, never the raw multi-page text.
    assert profile.evidence_graph[0].text == INVESTIGATION_ARGS["summary"]
    assert raw_text not in profile.evidence_graph[0].text
    assert result.stages[0] == "Mission Started"
    assert result.stages[-1] == "Investigation Complete"
    assert result.mission.delegations == []  # no delegation in Document Intelligence's flow


async def test_encrypted_document_leaves_profile_untouched_and_completes_gracefully(monkeypatch):
    async def fake_execute(self, *, content, filename="document.pdf", **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.FAILED,
            explanation="ENCRYPTED: this document is password-protected and cannot be read without one.",
        )

    monkeypatch.setattr(PDFReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([])  # never called — extraction fails before any reasoning
    profile = StudentProfile(student_id="s1")

    result = await investigate_document(
        "portfolio.pdf", b"irrelevant", student_id="s1", profile=profile, llm=llm,
    )

    assert result.status == ToolStatus.FAILED
    assert "ENCRYPTED" in result.explanation
    assert result.evidence_added is False
    assert profile.evidence_graph == []
    assert profile.notebook_entries == []
    # The mission itself still completes gracefully (never crashes) even
    # though the investigation stopped early — it just never reaches the
    # later stages that depend on a successful extraction.
    assert "Reading Document" in result.stages
    assert "Investigation Complete" not in result.stages
    assert result.mission.status == MissionStatus.COMPLETED


async def test_research_paper_routes_to_career_intelligence_not_discovery(monkeypatch):
    from aureon.agents.specialized.career_intelligence.tools import ResearchPaperReaderTool

    async def fake_execute(self, *, content, filename="research_paper.pdf", **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=filename, summary="Abstract Introduction Methodology " * 20)],
        )

    monkeypatch.setattr(ResearchPaperReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_document_investigation", INVESTIGATION_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_document(
        "Research_Paper.pdf", b"irrelevant", student_id="s1", profile=profile, llm=llm,
    )

    assert result.category == "research_paper"
    assert result.owning_specialist == AgentName.CAREER_INTELLIGENCE.value
    completed_agents = [a.name for a in build_mission_snapshot(result.mission).agents if a.status == "completed"]
    assert completed_agents == [AgentName.CAREER_INTELLIGENCE.value]
