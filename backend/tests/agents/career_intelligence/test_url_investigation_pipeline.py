from aureon.agents.specialized.career_intelligence.tools import URLReaderTool
from aureon.agents.specialized.career_intelligence.url_investigation_pipeline import investigate_url
from aureon.agents.tools.base import Evidence, ToolResult, ToolStatus
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import AgentName
from tests.fakes import FakeLLMClient, tool_call_response

GITHUB_URL = "https://github.com/someone/ml-project"
BLOG_URL = "https://random-blog.example.com/ai-careers"

INVESTIGATION_ARGS = {
    "title": "A Real Project",
    "summary": "A real, grounded summary of the fetched page.",
    "key_findings": ["Uses Python and PyTorch"],
    "structured_fields": {"languages": "Python"},
    "insufficient_content": False,
}


async def test_successful_fetch_with_delegation_appends_real_evidence(monkeypatch):
    async def fake_execute(self, *, url, **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=url, source_type="url", summary="Real fetched page text about a PyTorch project.")],
        )

    monkeypatch.setattr(URLReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_url_investigation", INVESTIGATION_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_url(GITHUB_URL, student_id="s1", profile=profile, llm=llm)

    assert result.delegated is True
    assert result.owning_specialist == AgentName.DISCOVERY.value
    assert result.status == ToolStatus.COMPLETED
    assert result.evidence_added is True
    assert len(profile.evidence_graph) == 1
    assert len(profile.notebook_entries) == 1
    assert result.stages[0] == "Mission Started"
    assert result.stages[-1] == "Investigation Complete"


async def test_failed_fetch_leaves_profile_completely_untouched(monkeypatch):
    async def fake_execute(self, *, url, **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.FAILED,
            explanation=f"{url} returned HTTP 404.",
        )

    monkeypatch.setattr(URLReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([])  # never called — fetch fails before any reasoning happens
    profile = StudentProfile(student_id="s1")

    result = await investigate_url(BLOG_URL, student_id="s1", profile=profile, llm=llm)

    assert result.status == ToolStatus.FAILED
    assert result.evidence_added is False
    assert profile.evidence_graph == []
    assert profile.notebook_entries == []
    assert "404" in result.explanation


async def test_unknown_category_defaults_to_career_intelligence_no_delegation(monkeypatch):
    async def fake_execute(self, *, url, **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.COMPLETED,
            evidence=[Evidence(source=url, source_type="url", summary="A real career article about AI research roles.")],
        )

    monkeypatch.setattr(URLReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_url_investigation", INVESTIGATION_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_url(BLOG_URL, student_id="s1", profile=profile, llm=llm)

    assert result.delegated is False
    assert result.owning_specialist == AgentName.CAREER_INTELLIGENCE.value


async def test_url_reader_tool_performs_a_real_network_fetch():
    """One genuine network test — example.com is IANA's reserved
    documentation/testing domain, stable and appropriate for this. If a
    future CI environment has no network egress, this test (and only
    this one) would need to be skipped there."""
    result = await URLReaderTool().execute(url="https://example.com")

    assert result.status == ToolStatus.COMPLETED
    assert len(result.evidence) == 1
    assert len(result.evidence[0].summary) > 0
