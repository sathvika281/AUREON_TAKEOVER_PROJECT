from aureon.agents.mission.mission import MissionStatus
from aureon.agents.specialized.discovery.github_pipeline import investigate_repository
from aureon.agents.specialized.discovery.tools import GitHubReaderTool
from aureon.agents.tools.base import Evidence, ToolResult, ToolStatus
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.types import AgentName
from tests.fakes import FakeLLMClient, tool_call_response

ANALYSIS_ARGS = {
    "overall_summary": "A well-structured project demonstrating solid engineering practices.",
    "project_purpose": "A backend service.",
    "technical_complexity": "Moderate.",
    "problem_solving": "Clear separation of concerns.",
    "code_organization": "Organized into modules.",
    "technology_breadth": "Uses several real technologies.",
    "documentation_quality": "Substantial README present.",
    "learning_signals": "Shows growth across commits.",
    "engineering_maturity": "Has tests and CI.",
    "research_orientation": "Not research-oriented.",
    "ai_ml_signals": "Uses PyTorch.",
    "insufficient_content": False,
}


def _completed_tool_result() -> ToolResult:
    return ToolResult(
        tool_name="github_reader", status=ToolStatus.COMPLETED,
        evidence=[Evidence(
            source="someone/myproject", source_type="github_repository", summary="fetched",
            metadata={
                "repo_data": {
                    "name": "myproject", "description": "desc", "owner": {"login": "someone"},
                    "language": "Python", "topics": ["ai", "backend"], "license": {"name": "MIT"},
                    "stargazers_count": 999, "forks_count": 50, "pushed_at": "2026-01-01T00:00:00Z",
                },
                "languages": {"Python": 1000},
                "readme_text": "x" * 500,
                "root_files": ["requirements.txt", "tests", ".github"],
                "dependency_names": ["pytorch"],
                "has_ci_workflows": True,
            },
        )],
    )


async def test_invalid_url_never_creates_a_tool_call_and_completes_gracefully():
    llm = FakeLLMClient([])
    profile = StudentProfile(student_id="s1")

    result = await investigate_repository(
        "https://gist.github.com/someone/abc", student_id="s1", profile=profile, llm=llm,
    )

    assert result.status == ToolStatus.FAILED
    assert "public GitHub repository" in result.explanation
    assert profile.evidence_graph == []
    assert result.mission.status == MissionStatus.COMPLETED


async def test_not_found_repository_leaves_profile_untouched(monkeypatch):
    async def fake_execute(self, *, owner, repo, **kwargs):
        return ToolResult(
            tool_name=self.name, status=ToolStatus.FAILED,
            explanation=f"'{owner}/{repo}' was not found.",
        )

    monkeypatch.setattr(GitHubReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([])
    profile = StudentProfile(student_id="s1")

    result = await investigate_repository(
        "https://github.com/someone/doesnotexist", student_id="s1", profile=profile, llm=llm,
    )

    assert result.status == ToolStatus.FAILED
    assert profile.evidence_graph == []
    assert profile.career_dna.traits == {}
    assert result.evidence_added is False


async def test_successful_investigation_updates_career_dna_and_records_skills(monkeypatch):
    async def fake_execute(self, *, owner, repo, **kwargs):
        return _completed_tool_result()

    monkeypatch.setattr(GitHubReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_github_investigation", ANALYSIS_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_repository(
        "https://github.com/someone/myproject", student_id="s1", profile=profile, llm=llm,
    )

    assert result.status == ToolStatus.COMPLETED
    assert result.evidence_added is True
    assert "Career DNA Updated" in result.artifacts_updated
    assert "Discovery Notebook Updated" in result.artifacts_updated
    # Real trait updates: has_tests + has_ci -> analytical_thinking; supporting infra -> motivation.
    assert "analytical_thinking" in profile.career_dna.traits
    assert "motivation" in profile.career_dna.traits
    # Skill evidence cites real repo signals.
    skill_texts = [e.text for e in profile.evidence_graph if "pytorch" in e.text.lower()]
    assert len(skill_texts) == 1
    assert result.mission.delegations == []  # Discovery owns this outright, no delegation
    completed_agents = [a for a in result.stages]
    assert "Investigation Complete" in completed_agents


async def test_popularity_metrics_never_drive_career_dna_updates(monkeypatch):
    """Even a repo with huge stars/forks but no real structural signals
    (no tests, no CI, no README, no build files) gets no Career DNA
    update from those alone."""
    async def fake_execute(self, *, owner, repo, **kwargs):
        return ToolResult(
            tool_name="github_reader", status=ToolStatus.COMPLETED,
            evidence=[Evidence(
                source="someone/famous", source_type="github_repository", summary="fetched",
                metadata={
                    "repo_data": {
                        "name": "famous", "description": "", "owner": {"login": "someone"},
                        "language": "Python", "topics": [], "license": None,
                        "stargazers_count": 500000, "forks_count": 90000, "pushed_at": "2026-01-01T00:00:00Z",
                    },
                    "languages": {"Python": 1000},
                    "readme_text": None,
                    "root_files": [],
                    "dependency_names": [],
                    "has_ci_workflows": False,
                },
            )],
        )

    monkeypatch.setattr(GitHubReaderTool, "execute", fake_execute)
    llm = FakeLLMClient([tool_call_response("record_github_investigation", ANALYSIS_ARGS)])
    profile = StudentProfile(student_id="s1")

    await investigate_repository(
        "https://github.com/someone/famous", student_id="s1", profile=profile, llm=llm,
    )

    assert "analytical_thinking" not in profile.career_dna.traits
    assert "communication" not in profile.career_dna.traits
    assert "motivation" not in profile.career_dna.traits
    # No evidence text anywhere should ever mention stars/forks.
    assert all("star" not in e.text.lower() and "fork" not in e.text.lower() for e in profile.evidence_graph)
