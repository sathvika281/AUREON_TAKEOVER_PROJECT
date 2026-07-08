from datetime import datetime, timezone

from aureon.agents.specialized.decision.simulation_pipeline import run_career_simulation
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.mentor_match import MentorMatch
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
CAREER_B = Career(id="robotics", name="Robotics Engineering", category="engineering", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)

SIMULATION_ARGS = {
    "learning_journey": "A grounded learning path.",
    "expected_milestones": ["Learn Python"],
    "timeline": [{"phase": "Year 1", "focus": "Core skills", "milestones": ["Projects"]}],
    "trade_offs": {"advantages": ["a"], "challenges": ["c"], "opportunities": ["o"], "sacrifices": ["s"], "uncertainties": ["u"]},
    "insufficient_evidence": False,
}
INSIGHTS_ARGS = {
    "strongest_match_career_id": "ai_research",
    "why": "AI Research aligns most with your evidence.",
    "possible_risks": ["Highly competitive field."],
    "questions_to_explore": ["Do you prefer research or applied work?"],
    "recommended_next_investigation": "Investigate real AI Research labs.",
    "insufficient_evidence": False,
}


def _profile_with_two_candidates() -> StudentProfile:
    profile = StudentProfile(student_id="s1")
    now = datetime.now(timezone.utc)
    profile.career_candidates.append(CareerCandidate(
        id="c1", career_id="ai_research", career_name="AI Research", why_it_matches="x", confidence=0.7,
        created_at=now, updated_at=now,
    ))
    profile.career_candidates.append(CareerCandidate(
        id="c2", career_id="robotics", career_name="Robotics Engineering", why_it_matches="x", confidence=0.6,
        created_at=now, updated_at=now,
    ))
    return profile


async def test_successful_simulation_persists_real_records():
    profile = _profile_with_two_candidates()
    profile.mentor_matches.append(MentorMatch(
        id="m1", mentor_id="mentor-1", mentor_name="Dr. Real Mentor", why_it_matches="x", confidence=0.8,
    ))
    llm = FakeLLMClient([
        tool_call_response("record_career_simulation", SIMULATION_ARGS),
        tool_call_response("record_career_simulation", SIMULATION_ARGS),
        tool_call_response("record_decision_insights", INSIGHTS_ARGS),
    ])

    result = await run_career_simulation(
        ["ai_research", "robotics"], student_id="s1", profile=profile, careers=[CAREER_A, CAREER_B], llm=llm,
    )

    assert result.status == "completed"
    assert result.evidence_added is True
    assert len(profile.career_simulations) == 1
    sim = profile.career_simulations[0]
    assert len(sim.simulations) == 2
    assert sim.decision_insights.strongest_match_career_id == "ai_research"
    assert "Dr. Real Mentor" in sim.decision_insights.recommended_mentors
    assert any(a.startswith("Compare") for a in sim.simulations[0].next_best_actions)
    assert any(dm.action_type == "simulated" for dm in profile.decision_memory)
    simulated_events = [e for e in profile.career_exploration_history if e.interaction_type == "simulated"]
    assert len(simulated_events) == 2
    assert result.mission.delegations == []  # Decision owns this outright


async def test_recommended_mentors_never_include_discarded_matches():
    profile = _profile_with_two_candidates()
    profile.mentor_matches.append(MentorMatch(
        id="m1", mentor_id="mentor-1", mentor_name="Discarded Mentor", why_it_matches="x", confidence=0.99,
        status="discarded",
    ))
    llm = FakeLLMClient([
        tool_call_response("record_career_simulation", SIMULATION_ARGS),
        tool_call_response("record_career_simulation", SIMULATION_ARGS),
        tool_call_response("record_decision_insights", INSIGHTS_ARGS),
    ])

    result = await run_career_simulation(
        ["ai_research", "robotics"], student_id="s1", profile=profile, careers=[CAREER_A, CAREER_B], llm=llm,
    )

    assert "Discarded Mentor" not in result.simulation.decision_insights.recommended_mentors


async def test_insufficient_evidence_leaves_profile_untouched():
    profile = _profile_with_two_candidates()
    llm = FakeLLMClient([])  # every call falls back to no-tool-call insufficiency

    result = await run_career_simulation(
        ["ai_research", "robotics"], student_id="s1", profile=profile, careers=[CAREER_A, CAREER_B], llm=llm,
    )

    assert result.status == "insufficient_evidence"
    assert result.evidence_added is False
    assert profile.career_simulations == []
    assert profile.decision_memory == []
    assert profile.career_exploration_history == []
