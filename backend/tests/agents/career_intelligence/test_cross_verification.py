from aureon.agents.specialized.career_intelligence.cross_verification import analyze_evidence
from aureon.agents.tools.base import Evidence
from tests.fakes import FakeLLMClient, tool_call_response

EVIDENCE = [
    Evidence(source="https://en.wikipedia.org/wiki/Cybersecurity", source_type="wikipedia", title="Cybersecurity", summary="Cybersecurity is a growing field."),
    Evidence(source="https://arxiv.org/abs/1234", source_type="arxiv", title="A Paper", summary="Research on cybersecurity threats."),
]

FINDINGS_ARGS = {
    "overall_summary": "Cybersecurity demand appears strong across sources.",
    "findings": [
        {"claim": "Cybersecurity demand is growing", "status": "supported", "citing_sources": ["https://en.wikipedia.org/wiki/Cybersecurity"], "explanation": "Both sources agree demand is rising."},
    ],
    "agreements": ["Sources agree demand is rising."],
    "disagreements": [],
    "related_career_id": "career-123",
    "insufficient_evidence": False,
}


async def test_analyze_evidence_only_cites_real_provided_evidence():
    llm = FakeLLMClient([tool_call_response("record_career_investigation", FINDINGS_ARGS)])

    output = await analyze_evidence(
        "Is cybersecurity in demand?", EVIDENCE, known_candidates=[("career-123", "Cybersecurity")], llm=llm,
    )

    assert output.findings[0].status == "supported"
    sent_context = llm.calls[0]["messages"][1].content
    assert "Cybersecurity is a growing field." in sent_context
    assert "Research on cybersecurity threats." in sent_context


async def test_related_career_id_only_set_when_it_matches_known_candidates():
    args = dict(FINDINGS_ARGS, related_career_id="invented-id-not-real")
    llm = FakeLLMClient([tool_call_response("record_career_investigation", args)])

    output = await analyze_evidence(
        "Is cybersecurity in demand?", EVIDENCE, known_candidates=[("career-123", "Cybersecurity")], llm=llm,
    )

    assert output.related_career_id is None


async def test_related_career_id_kept_when_it_matches():
    llm = FakeLLMClient([tool_call_response("record_career_investigation", FINDINGS_ARGS)])

    output = await analyze_evidence(
        "Is cybersecurity in demand?", EVIDENCE, known_candidates=[("career-123", "Cybersecurity")], llm=llm,
    )

    assert output.related_career_id == "career-123"


async def test_analyze_evidence_degrades_gracefully_on_provider_error():
    class RaisingLLM:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("provider error")

    output = await analyze_evidence("Is cybersecurity in demand?", EVIDENCE, known_candidates=[], llm=RaisingLLM())

    assert output.insufficient_evidence is True
    assert output.findings == []


async def test_analyze_evidence_degrades_gracefully_on_no_tool_call():
    llm = FakeLLMClient([])  # no tool call

    output = await analyze_evidence("Is cybersecurity in demand?", EVIDENCE, known_candidates=[], llm=llm)

    assert output.insufficient_evidence is True
