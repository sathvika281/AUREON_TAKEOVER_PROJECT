from aureon.agents.specialized.career_intelligence.url_investigation import (
    _extraction_confidence,
    analyze_url_content,
    finalize_url_evidence,
)
from tests.fakes import FakeLLMClient, tool_call_response


def test_confidence_ceiling_ignores_short_extractions_regardless_of_claims():
    # Even if a downstream caller claimed high confidence, the ceiling is
    # driven only by real extracted-text length.
    assert _extraction_confidence(50) == 0.1
    assert _extraction_confidence(3000) == 0.9
    assert _extraction_confidence(3000) >= _extraction_confidence(1500) >= _extraction_confidence(200)


async def test_analyze_url_content_parses_structured_output():
    args = {
        "title": "Careers in AI Research",
        "summary": "An overview of what AI researchers do day to day.",
        "key_findings": ["Requires strong math background", "Publishing is central to the role"],
        "structured_fields": {"required_skills": "math, ML, research writing"},
        "insufficient_content": False,
    }
    llm = FakeLLMClient([tool_call_response("record_url_investigation", args)])

    output = await analyze_url_content(
        category="career_article", raw_text="AI researchers spend their days...", url="https://example.com/ai-careers", llm=llm,
    )

    assert output.title == "Careers in AI Research"
    assert "math" in output.structured_fields["required_skills"]


def test_finalize_url_evidence_merges_real_confidence_with_llm_narrative():
    from aureon.agents.specialized.career_intelligence.url_investigation import UrlInvestigationTurnOutput

    output = UrlInvestigationTurnOutput(
        title="x", summary="a real summary", key_findings=["finding one"],
        structured_fields={"topic": "AI"},
    )
    raw_text = "x" * 3000

    evidence = finalize_url_evidence(category="research_paper", url="https://arxiv.org/abs/1", raw_text=raw_text, output=output)

    assert evidence.confidence == 0.9  # long real extraction -> ceiling, not LLM-asserted
    assert evidence.source_type == "url:research_paper"
    assert evidence.metadata["key_findings"] == ["finding one"]
