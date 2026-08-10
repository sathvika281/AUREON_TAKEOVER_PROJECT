from aureon.agents.specialized.decision.simulation_alignment import AlignmentFacts
from aureon.agents.specialized.decision.simulation_reasoning import (
    analyze_career_simulation,
    analyze_decision_insights,
)
from aureon.agents.specialized.growth.evidence_summary import assemble_progress_evidence
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)
CAREER_A = Career(id="ai_research", name="AI Research", category="research", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)
CAREER_B = Career(id="robotics", name="Robotics Engineering", category="traditional", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)

ALIGNMENT = AlignmentFacts(career_dna_alignment="Strong — x", student_interest_alignment="x", evidence_confidence="Strong (1 supporting, 0 contradicting)")

SIMULATION_ARGS = {
    "learning_journey": "A grounded learning path.",
    "expected_milestones": ["Learn Python", "Build a project"],
    "timeline": [{"phase": "Year 1", "focus": "Core skills", "milestones": ["Projects"]}],
    "trade_offs": {"advantages": ["a"], "challenges": ["c"], "opportunities": ["o"], "sacrifices": ["s"], "uncertainties": ["u"]},
    "insufficient_evidence": False,
}


async def test_analyze_career_simulation_parses_real_output():
    llm = FakeLLMClient([tool_call_response("record_career_simulation", SIMULATION_ARGS)])
    profile = StudentProfile(student_id="s1")
    progress = assemble_progress_evidence(profile)

    output = await analyze_career_simulation(
        CAREER_A, {}, ALIGNMENT, career_dna=CareerDNA(), progress=progress, llm=llm,
    )

    assert output.learning_journey == "A grounded learning path."
    assert output.timeline[0].phase == "Year 1"


async def test_independent_simulation_never_mentions_other_careers():
    llm = FakeLLMClient([tool_call_response("record_career_simulation", SIMULATION_ARGS)])
    profile = StudentProfile(student_id="s1")
    progress = assemble_progress_evidence(profile)

    await analyze_career_simulation(CAREER_A, {}, ALIGNMENT, career_dna=CareerDNA(), progress=progress, llm=llm)

    sent = llm.calls[0]["messages"]
    full_text = " ".join(m.content for m in sent)
    assert CAREER_B.name not in full_text
    assert CAREER_A.name in full_text


async def test_analyze_career_simulation_degrades_gracefully_on_provider_error():
    class RaisingLLM:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("provider error")

    profile = StudentProfile(student_id="s1")
    progress = assemble_progress_evidence(profile)
    output = await analyze_career_simulation(CAREER_A, {}, ALIGNMENT, career_dna=CareerDNA(), progress=progress, llm=RaisingLLM())

    assert output.insufficient_evidence is True


INSIGHTS_ARGS = {
    "strongest_match_career_id": "invented-not-real",
    "why": "x", "possible_risks": [], "questions_to_explore": [],
    "recommended_next_investigation": "x", "insufficient_evidence": False,
}


async def test_decision_insights_clears_invented_career_id():
    llm = FakeLLMClient([tool_call_response("record_decision_insights", INSIGHTS_ARGS)])
    entries = [
        ("ai_research", "AI Research", await analyze_career_simulation(
            CAREER_A, {}, ALIGNMENT, career_dna=CareerDNA(),
            progress=assemble_progress_evidence(StudentProfile(student_id="s1")),
            llm=FakeLLMClient([tool_call_response("record_career_simulation", SIMULATION_ARGS)]),
        )),
    ]

    output = await analyze_decision_insights(entries, llm=llm)

    assert output.strongest_match_career_id is None


async def test_decision_insights_keeps_valid_career_id():
    args = dict(INSIGHTS_ARGS, strongest_match_career_id="ai_research")
    llm = FakeLLMClient([tool_call_response("record_decision_insights", args)])
    sim_llm = FakeLLMClient([tool_call_response("record_career_simulation", SIMULATION_ARGS)])
    output_a = await analyze_career_simulation(
        CAREER_A, {}, ALIGNMENT, career_dna=CareerDNA(),
        progress=assemble_progress_evidence(StudentProfile(student_id="s1")), llm=sim_llm,
    )
    entries = [("ai_research", "AI Research", output_a)]

    output = await analyze_decision_insights(entries, llm=llm)

    assert output.strongest_match_career_id == "ai_research"
