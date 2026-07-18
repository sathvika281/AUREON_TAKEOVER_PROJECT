from aureon.agents.specialized.opportunity import agent as agent_module
from aureon.agents.specialized.opportunity.agent import OpportunityAgent
from aureon.domain.models.opportunity_fit import FitFactor, OpportunityFitResult
from aureon.domain.models.student_profile import StudentProfile
from tests.agents.opportunity._factories import make_opportunity
from tests.fakes import FakeLLMClient, tool_call_response


async def test_find_opportunities_insufficient_evidence_skips_the_llm():
    agent = OpportunityAgent()
    llm = FakeLLMClient()
    profile = StudentProfile(student_id="s1")

    output = await agent.find_opportunities(profile, [], llm=llm)

    assert output.insufficient_evidence is True
    assert llm.calls == []


async def test_find_opportunities_returns_ranked_recommendation_with_real_narrative():
    agent = OpportunityAgent()
    opportunity = make_opportunity()
    narrative_args = {
        "narratives": [
            {
                "opportunity_id": opportunity.id,
                "why_recommended": "Matches your stated interests.",
                "recommended_preparation": "Keep building real evidence.",
            }
        ]
    }
    llm = FakeLLMClient([tool_call_response("record_opportunity_narratives", narrative_args)])
    profile = StudentProfile(student_id="s1")

    output = await agent.find_opportunities(profile, [opportunity], llm=llm)

    assert len(output.recommendations) == 1
    rec = output.recommendations[0]
    assert rec.fit.rank == 1
    assert rec.preparation.why_recommended == "Matches your stated interests."
    assert len(llm.calls) == 1


async def test_find_opportunities_falls_back_to_deterministic_narrative_without_a_tool_call():
    agent = OpportunityAgent()
    opportunity = make_opportunity()
    llm = FakeLLMClient()  # nothing queued -> empty tool_calls
    profile = StudentProfile(student_id="s1")

    output = await agent.find_opportunities(profile, [opportunity], llm=llm)

    assert output.recommendations[0].preparation.why_recommended


async def test_evaluate_fit_is_deterministically_repeatable():
    agent = OpportunityAgent()
    opportunity = make_opportunity()
    profile = StudentProfile(student_id="s1")

    first = await agent.evaluate_fit(profile, opportunity)
    profile.foundation_memory.opportunities.score_history.pop(opportunity.id)  # isolate from smoothing across calls
    second = await agent.evaluate_fit(profile, opportunity)

    assert first.overall_score == second.overall_score
    assert first.readiness_label == second.readiness_label


def _fake_fit(opportunity_id: str, overall_score: float, alignment_score: float) -> OpportunityFitResult:
    factors = [
        FitFactor(key="career_alignment", label="Career Alignment", score=alignment_score, weight=0.15, data_available=True, rationale="x", evidence=["e"]),
        FitFactor(key="career_goal_alignment", label="Career Goal Alignment", score=alignment_score, weight=0.05, data_available=True, rationale="x", evidence=["e"]),
    ]
    return OpportunityFitResult(
        opportunity_id=opportunity_id, overall_score=overall_score, confidence=0.8,
        confidence_basis={"smoothed": False}, readiness_label="ready", factors=factors,
        requirements_met=3, requirements_total=5,
    )


async def test_trajectory_tie_break_prefers_stronger_alignment_for_near_equal_scores(monkeypatch):
    opp_a = make_opportunity(id="a", category="internship")
    opp_b = make_opportunity(id="b", category="internship")

    def fake_score_opportunity(profile, memory, opportunity, *, now, previous_score=None):
        if opportunity.id == "a":
            return _fake_fit("a", overall_score=0.700, alignment_score=0.9)
        return _fake_fit("b", overall_score=0.704, alignment_score=0.2)

    monkeypatch.setattr(agent_module, "score_opportunity", fake_score_opportunity)

    agent = OpportunityAgent()
    profile = StudentProfile(student_id="s1")
    output = await agent.find_opportunities(profile, [opp_b, opp_a], llm=FakeLLMClient(), top_n=2)

    # opp_b's raw overall_score (0.704) is slightly higher than opp_a's
    # (0.700), but both round to 0.70 — "similar fit" — so the tie-break
    # must promote opp_a for its far stronger career alignment.
    assert [r.opportunity.id for r in output.recommendations] == ["a", "b"]


async def test_trajectory_tie_break_does_not_override_a_real_score_gap(monkeypatch):
    opp_a = make_opportunity(id="a", category="internship")
    opp_b = make_opportunity(id="b", category="internship")

    def fake_score_opportunity(profile, memory, opportunity, *, now, previous_score=None):
        if opportunity.id == "a":
            return _fake_fit("a", overall_score=0.50, alignment_score=0.9)
        return _fake_fit("b", overall_score=0.90, alignment_score=0.1)

    monkeypatch.setattr(agent_module, "score_opportunity", fake_score_opportunity)

    agent = OpportunityAgent()
    profile = StudentProfile(student_id="s1")
    output = await agent.find_opportunities(profile, [opp_a, opp_b], llm=FakeLLMClient(), top_n=2)

    # A genuine 0.40 gap is not "similar fit" — opp_b's real overall_score
    # advantage must win regardless of career alignment.
    assert [r.opportunity.id for r in output.recommendations] == ["b", "a"]
