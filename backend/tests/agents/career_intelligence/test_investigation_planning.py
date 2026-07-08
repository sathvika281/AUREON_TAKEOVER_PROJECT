from aureon.agents.specialized.career_intelligence.investigation_planning import plan_investigation
from tests.fakes import FakeLLMClient, tool_call_response

PLAN_ARGS = {
    "wikipedia_query": "cybersecurity career overview",
    "arxiv_query": "cybersecurity research trends",
    "semantic_scholar_query": "cybersecurity career outlook",
    "rationale": "Broad overview plus academic research angle.",
}


async def test_plan_investigation_uses_only_the_real_question_and_candidates():
    llm = FakeLLMClient([tool_call_response("record_investigation_plan", PLAN_ARGS)])

    plan = await plan_investigation(
        "Is Cybersecurity better than AI in 2035?", known_candidates=["AI Research"], llm=llm,
    )

    assert plan.wikipedia_query == PLAN_ARGS["wikipedia_query"]
    assert plan.arxiv_query == PLAN_ARGS["arxiv_query"]
    assert plan.semantic_scholar_query == PLAN_ARGS["semantic_scholar_query"]
    sent = llm.calls[0]["messages"]
    system_content = sent[0].content
    assert "Is Cybersecurity better than AI in 2035?" in sent[1].content
    assert "AI Research" in system_content


async def test_plan_investigation_falls_back_when_no_tool_call():
    llm = FakeLLMClient([])  # no tool call returned

    plan = await plan_investigation("Should I pursue AI Research?", known_candidates=[], llm=llm)

    assert plan.wikipedia_query == "Should I pursue AI Research?"
    assert plan.arxiv_query == "Should I pursue AI Research?"
    assert plan.semantic_scholar_query == "Should I pursue AI Research?"


async def test_plan_investigation_falls_back_on_malformed_arguments():
    llm = FakeLLMClient([tool_call_response("record_investigation_plan", {"wikipedia_query": 123})])

    plan = await plan_investigation("Which countries lead AI research?", known_candidates=[], llm=llm)

    assert plan.wikipedia_query == "Which countries lead AI research?"
    assert "could not run" in plan.rationale
