from datetime import datetime, timezone

import aureon.agents.specialized.career_intelligence.agent as agent_module
from aureon.agents.specialized.career_intelligence.agent import CareerIntelligenceAgent
from aureon.agents.state import new_state
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_dna import CareerDNA, TraitSignal
from aureon.domain.models.student_profile import StudentProfile
from tests.fakes import FakeLLMClient, tool_call_response

SAMPLE_CAREER = Career(
    id="ai_research_scientist",
    name="AI Research Scientist",
    category="research",
    industry="technology",
    one_liner="Researches new machine learning methods.",
    trait_tags=["curiosity", "analytical_thinking"],
    reality=CareerReality(
        daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
        research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
        stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
        required_education="x",
    ),
    future_lens=FutureLens(
        ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
        emerging_opportunities="x", timeline_narrative="x",
    ),
)

BASE_ARGS = {
    "reply_to_student": "Here's what I found that might fit.",
    "candidates": [
        {
            "career_id": "ai_research_scientist",
            "why_it_matches": "You've repeatedly described losing track of time investigating open-ended technical questions.",
            "supporting_evidence": ["loves open-ended research"],
            "contradicting_evidence": [],
            "missing_evidence": ["exposure to a real research environment"],
            "confidence": 0.7,
            "uncertainty_reason": None,
        }
    ],
    "insufficient_evidence": False,
    "insufficient_evidence_reason": None,
}


class _FakeCareerRepository:
    def __init__(self, careers: list[Career]):
        self._careers = careers

    async def list_careers(self, **_kwargs) -> list[Career]:
        return self._careers


def _profile_with_traits() -> StudentProfile:
    profile = StudentProfile(student_id="s1")
    profile.career_dna = CareerDNA(
        traits={"curiosity": TraitSignal(score=0.8, summary="Very curious", updated_at=datetime.now(timezone.utc))}
    )
    return profile


async def test_run_creates_candidate_with_evidence_and_notebook_entry(monkeypatch):
    monkeypatch.setattr(agent_module, "CareerRepository", lambda: _FakeCareerRepository([SAMPLE_CAREER]))
    llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", BASE_ARGS)])

    state = new_state(conversation_id="c1", student_id="s1", student_profile=_profile_with_traits())
    result = await CareerIntelligenceAgent().run(state, llm=llm)

    profile = result["student_profile"]
    assert len(profile.career_candidates) == 1
    candidate = profile.career_candidates[0]
    assert candidate.career_id == "ai_research_scientist"
    assert candidate.career_name == "AI Research Scientist"

    supporting = [e for e in profile.evidence_graph if e.related_career == "ai_research_scientist" and e.relation == "supports"]
    assert len(supporting) == 1
    assert supporting[0].text == "loves open-ended research"

    belief_revisions = [e for e in profile.notebook_entries if e.kind == "belief_revision" and e.related_career == "ai_research_scientist"]
    assert len(belief_revisions) == 1


async def test_confidence_is_capped_when_no_supporting_evidence(monkeypatch):
    monkeypatch.setattr(agent_module, "CareerRepository", lambda: _FakeCareerRepository([SAMPLE_CAREER]))
    args = {**BASE_ARGS, "candidates": [{**BASE_ARGS["candidates"][0], "supporting_evidence": [], "confidence": 0.95}]}
    llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", args)])

    state = new_state(conversation_id="c1", student_id="s1", student_profile=_profile_with_traits())
    result = await CareerIntelligenceAgent().run(state, llm=llm)

    candidate = result["student_profile"].career_candidates[0]
    assert candidate.confidence <= 0.2


async def test_insufficient_evidence_produces_no_candidates(monkeypatch):
    monkeypatch.setattr(agent_module, "CareerRepository", lambda: _FakeCareerRepository([SAMPLE_CAREER]))
    args = {
        "reply_to_student": "Let's explore a bit more before looking at specific careers.",
        "candidates": [],
        "insufficient_evidence": True,
        "insufficient_evidence_reason": "Only one trait recorded so far.",
    }
    llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", args)])

    state = new_state(conversation_id="c1", student_id="s1", student_profile=StudentProfile(student_id="s1"))
    result = await CareerIntelligenceAgent().run(state, llm=llm)

    assert result["student_profile"].career_candidates == []
    payload = result["agent_outputs"][CareerIntelligenceAgent.name].payload
    assert payload["insufficient_evidence"] is True


async def test_contradicting_evidence_lowers_recorded_confidence(monkeypatch):
    monkeypatch.setattr(agent_module, "CareerRepository", lambda: _FakeCareerRepository([SAMPLE_CAREER]))
    args = {
        **BASE_ARGS,
        "candidates": [
            {
                **BASE_ARGS["candidates"][0],
                "contradicting_evidence": ["said they dislike long isolated research stretches"],
                "confidence": 0.7,
            }
        ],
    }
    llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", args)])

    state = new_state(conversation_id="c1", student_id="s1", student_profile=_profile_with_traits())
    result = await CareerIntelligenceAgent().run(state, llm=llm)

    profile = result["student_profile"]
    contradicting = [e for e in profile.evidence_graph if e.relation == "contradicts"]
    assert len(contradicting) == 1
    # Recorded confidence must be strictly lower than the LLM's own stated value
    # given real contradicting evidence.
    assert profile.career_candidates[0].confidence < 0.7


async def test_candidate_absent_from_a_later_analysis_is_discarded_not_deleted(monkeypatch):
    monkeypatch.setattr(agent_module, "CareerRepository", lambda: _FakeCareerRepository([SAMPLE_CAREER]))
    profile = _profile_with_traits()

    first_llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", BASE_ARGS)])
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    result = await CareerIntelligenceAgent().run(state, llm=first_llm)
    profile = result["student_profile"]
    assert profile.career_candidates[0].status == "active"

    second_args = {**BASE_ARGS, "candidates": []}
    second_llm = FakeLLMClient([tool_call_response("record_career_intelligence_analysis", second_args)])
    state["student_profile"] = profile
    result = await CareerIntelligenceAgent().run(state, llm=second_llm)

    profile = result["student_profile"]
    # Kept, not deleted, so its history survives.
    assert len(profile.career_candidates) == 1
    assert profile.career_candidates[0].status == "discarded"
    assert profile.career_candidates[0].transition_reason is not None
    discard_entries = [
        e for e in profile.notebook_entries
        if e.kind == "belief_revision" and e.updated_belief == "discarded" and e.related_career == "ai_research_scientist"
    ]
    assert len(discard_entries) == 1
