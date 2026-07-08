from datetime import datetime, timezone

from aureon.agents.specialized.decision.reasoning import (
    analyze_comparison,
    analyze_parallel_universe,
    finalize_comparison,
    finalize_parallel_universe,
)
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x", entrepreneurship_potential="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)

CAREER_A = Career(id="ai_research", name="AI Research", category="research", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)
CAREER_B = Career(id="ux_research", name="UX Research", category="interdisciplinary", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)


async def test_analyze_comparison_parses_dimension_reasoning():
    args = {
        "reply_to_student": "Here's how they compare.",
        "dimension_reasoning": [{"dimension": "creativity", "why_it_matters_to_you": "You value creative problem-solving."}],
        "summary_reason": "Both fit your curiosity, but AI Research leans more research-heavy.",
        "missing_evidence": ["work-life balance preference"],
    }
    llm = FakeLLMClient([tool_call_response("record_career_comparison", args)])
    profile = StudentProfile(student_id="s1")

    output = await analyze_comparison(profile, [CAREER_A, CAREER_B], llm=llm)

    assert output.summary_reason == args["summary_reason"]
    assert output.dimension_reasoning[0].dimension == "creativity"


def test_finalize_comparison_uses_real_facts_not_llm_echo():
    args = {
        "reply_to_student": "x",
        "dimension_reasoning": [{"dimension": "creativity", "why_it_matters_to_you": "personalized reason"}],
        "summary_reason": "summary",
        "missing_evidence": [],
    }
    from aureon.agents.specialized.decision.schemas import ComparisonTurnOutput
    output = ComparisonTurnOutput.model_validate(args)

    comparison = finalize_comparison(["ai_research", "ux_research"], [CAREER_A, CAREER_B], output, datetime.now(timezone.utc))

    creativity_dim = next(d for d in comparison.dimensions if d.dimension == "creativity")
    assert creativity_dim.per_career["ai_research"] == "x"  # real fact from CareerReality, not from the LLM
    assert creativity_dim.why_it_matters_to_you == "personalized reason"
    # A dimension the LLM didn't cover still gets a real per_career fact plus an honest fallback narrative.
    other_dim = next(d for d in comparison.dimensions if d.dimension == "stress")
    assert other_dim.per_career["ai_research"] == "x"
    assert "No specific personalization" in other_dim.why_it_matters_to_you


async def test_analyze_parallel_universe_returns_two_branches():
    args = {
        "reply_to_student": "x",
        "branches": [
            {"career_id": "ai_research", "daily_work": "d1", "lifestyle": "l1", "growth": "g1", "challenges": "c1", "future_opportunities": "f1"},
            {"career_id": "ux_research", "daily_work": "d2", "lifestyle": "l2", "growth": "g2", "challenges": "c2", "future_opportunities": "f2"},
        ],
        "missing_evidence": [],
    }
    llm = FakeLLMClient([tool_call_response("record_parallel_universe_scenario", args)])
    profile = StudentProfile(student_id="s1")

    output = await analyze_parallel_universe(profile, [CAREER_A, CAREER_B], llm=llm)

    assert len(output.branches) == 2


def test_finalize_parallel_universe_always_frames_as_not_a_prediction():
    from aureon.agents.specialized.decision.schemas import ParallelUniverseTurnOutput
    output = ParallelUniverseTurnOutput.model_validate({
        "reply_to_student": "x",
        "branches": [
            {"career_id": "ai_research", "daily_work": "d", "lifestyle": "l", "growth": "g", "challenges": "c", "future_opportunities": "f"},
        ],
        "missing_evidence": [],
    })
    scenario = finalize_parallel_universe(output, {"ai_research": "AI Research"}, datetime.now(timezone.utc))
    assert "not a prediction" in scenario.framing_note.lower()
    assert scenario.branches[0].career_name == "AI Research"
