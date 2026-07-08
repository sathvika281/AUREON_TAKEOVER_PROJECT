from aureon.agents.specialized.career_intelligence.search_investigation_pipeline import investigate_question
from aureon.agents.specialized.career_intelligence.search_sources import SourceSearchOutcome, SourceResult
from aureon.agents.specialized.career_intelligence.tools import MultiSourceSearchTool
from aureon.agents.tools.base import Evidence, ToolResult, ToolStatus
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

PLAN_ARGS = {
    "wikipedia_query": "cybersecurity career outlook",
    "arxiv_query": "cybersecurity research trends",
    "semantic_scholar_query": "cybersecurity career research",
    "rationale": "Broad overview plus academic angle.",
}

FINDINGS_ARGS = {
    "overall_summary": "Cybersecurity demand appears strong across sources.",
    "findings": [
        {"claim": "Cybersecurity demand is growing", "status": "supported", "citing_sources": ["wikipedia"], "explanation": "Sources agree demand is rising."},
        {"claim": "Unclear if a masters is required", "status": "insufficient_evidence", "citing_sources": [], "explanation": "No source addressed this directly."},
    ],
    "agreements": ["Demand is rising."],
    "disagreements": [],
    "related_career_id": None,
    "insufficient_evidence": False,
}

REAL_EVIDENCE = [
    Evidence(source="https://en.wikipedia.org/wiki/Cybersecurity", source_type="wikipedia", title="Cybersecurity", summary="Cybersecurity is a growing field."),
    Evidence(source="https://arxiv.org/abs/1234", source_type="arxiv", title="A Paper", summary="Research on cybersecurity threats."),
]


def _patch_execute(monkeypatch, tool_result: ToolResult, outcomes: dict[str, SourceSearchOutcome]):
    async def fake_execute(self, *, wikipedia_query, arxiv_query, semantic_scholar_query, **kwargs):
        self.last_outcomes = outcomes
        return tool_result

    monkeypatch.setattr(MultiSourceSearchTool, "execute", fake_execute)


def _two_source_outcomes(rate_limited: bool) -> dict[str, SourceSearchOutcome]:
    return {
        "wikipedia": SourceSearchOutcome(status="completed", results=[
            SourceResult(title="Cybersecurity", url="https://en.wikipedia.org/wiki/Cybersecurity", snippet="x", source_type="wikipedia"),
        ]),
        "arxiv": SourceSearchOutcome(status="completed", results=[
            SourceResult(title="A Paper", url="https://arxiv.org/abs/1234", snippet="y", source_type="arxiv"),
        ]),
        "semantic_scholar": SourceSearchOutcome(
            status="rate_limited" if rate_limited else "no_results",
            explanation="Semantic Scholar's API rate limit was reached." if rate_limited else "No results.",
        ),
    }


async def test_successful_investigation_records_evidence_notebook_and_investigation(monkeypatch):
    outcomes = _two_source_outcomes(rate_limited=True)
    _patch_execute(monkeypatch, ToolResult(tool_name="multi_source_search", status=ToolStatus.COMPLETED, evidence=REAL_EVIDENCE), outcomes)
    llm = FakeLLMClient([
        tool_call_response("record_investigation_plan", PLAN_ARGS),
        tool_call_response("record_career_investigation", FINDINGS_ARGS),
    ])
    profile = StudentProfile(student_id="s1")

    result = await investigate_question("Should I pursue Cybersecurity?", student_id="s1", profile=profile, llm=llm)

    assert result.status == ToolStatus.COMPLETED
    assert result.evidence_added is True
    assert "Evidence Graph Updated" in result.artifacts_updated
    assert "Discovery Notebook Updated" in result.artifacts_updated
    assert "Career Investigations Updated" in result.artifacts_updated
    assert len(profile.evidence_graph) == 1  # only the "supported" finding, not the insufficient_evidence one
    assert len(profile.notebook_entries) == 1
    assert len(profile.career_investigations) == 1
    assert result.mission.delegations == []  # Career Intelligence owns this outright
    assert result.stages[0] == "Mission Created"
    assert result.stages[-1] == "Investigation Complete"
    assert result.source_availability.sources_retrieved == 2
    assert result.source_availability.sources_unavailable == 1


async def test_all_sources_failed_leaves_profile_untouched(monkeypatch):
    outcomes = {
        "wikipedia": SourceSearchOutcome(status="failed", explanation="Wikipedia timed out."),
        "arxiv": SourceSearchOutcome(status="failed", explanation="arXiv timed out."),
        "semantic_scholar": SourceSearchOutcome(status="rate_limited", explanation="Rate limited."),
    }
    _patch_execute(monkeypatch, ToolResult(tool_name="multi_source_search", status=ToolStatus.FAILED, explanation="No real evidence could be retrieved from any source."), outcomes)
    llm = FakeLLMClient([tool_call_response("record_investigation_plan", PLAN_ARGS)])
    profile = StudentProfile(student_id="s1")

    result = await investigate_question("Should I pursue Cybersecurity?", student_id="s1", profile=profile, llm=llm)

    assert result.status == ToolStatus.FAILED
    assert result.evidence_added is False
    assert profile.evidence_graph == []
    assert profile.notebook_entries == []
    assert profile.career_investigations == []
    assert result.source_availability.sources_retrieved == 0
    assert result.source_availability.sources_unavailable == 3


async def test_source_availability_never_leaks_into_the_reasoning_prompt(monkeypatch):
    """Two investigations with identical real evidence but different
    source availability (one with Semantic Scholar rate-limited, one with
    it simply returning no results) must send an identical reasoning
    prompt — availability is display-only metadata."""
    for rate_limited in (True, False):
        outcomes = _two_source_outcomes(rate_limited=rate_limited)
        _patch_execute(monkeypatch, ToolResult(tool_name="multi_source_search", status=ToolStatus.COMPLETED, evidence=REAL_EVIDENCE), outcomes)
        llm = FakeLLMClient([
            tool_call_response("record_investigation_plan", PLAN_ARGS),
            tool_call_response("record_career_investigation", FINDINGS_ARGS),
        ])
        profile = StudentProfile(student_id="s1")

        await investigate_question("Should I pursue Cybersecurity?", student_id="s1", profile=profile, llm=llm)

        cross_verification_call = llm.calls[1]
        prompt_text = " ".join(m.content for m in cross_verification_call["messages"])
        assert "rate limit" not in prompt_text.lower()
        assert "semantic scholar" not in prompt_text.lower()


async def test_related_career_id_only_matches_known_active_candidates(monkeypatch):
    outcomes = _two_source_outcomes(rate_limited=False)
    _patch_execute(monkeypatch, ToolResult(tool_name="multi_source_search", status=ToolStatus.COMPLETED, evidence=REAL_EVIDENCE), outcomes)
    args = dict(FINDINGS_ARGS, related_career_id="career-abc")
    llm = FakeLLMClient([
        tool_call_response("record_investigation_plan", PLAN_ARGS),
        tool_call_response("record_career_investigation", args),
    ])
    profile = StudentProfile(student_id="s1")
    profile.career_candidates.append(CareerCandidate(
        id="c1", career_id="career-abc", career_name="Cybersecurity Analyst", why_it_matches="x", confidence=0.5,
    ))

    result = await investigate_question("Should I pursue Cybersecurity?", student_id="s1", profile=profile, llm=llm)

    assert result.related_career_id == "career-abc"
    assert profile.evidence_graph[0].related_career == "career-abc"
