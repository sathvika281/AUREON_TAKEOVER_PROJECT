from langchain_core.messages import HumanMessage

from aureon.agents.specialized.discovery.agent import DiscoveryAgent, WHY_PROBE_DEPTH_CAP
from aureon.agents.state import new_state
from aureon.domain.models.student_profile import ExplorationEvent, StudentProfile
from aureon.shared.types import Mode
from tests.fakes import FakeLLMClient, tool_call_response

BASE_ARGS = {
    "reply_to_student": "That's interesting — what drew you to that?",
    "extracted_evidence": [
        {"kind": "conversation", "description": "Enjoys solving open-ended problems"}
    ],
    "career_dna_updates": [
        {
            "trait": "curiosity",
            "score": 0.7,
            "summary": "High curiosity",
            "rationale": "Said they love figuring out how things work",
        }
    ],
    "probe": {"is_probing": False, "topic": "", "depth": 0},
    "reflection_prompt": None,
    "hypotheses": [
        {
            "career_name": "AI Research",
            "confidence": 0.3,
            "supporting_evidence": ["curiosity"],
            "missing_evidence": ["leadership"],
            "contradicting_evidence": [],
        }
    ],
    "confidence_score": 0.5,
    "suggested_activity": None,
}


def _state_with_message(text: str = "I love figuring out how things work"):
    state = new_state(conversation_id="c1", student_id="s1")
    state["messages"] = [HumanMessage(content=text)]
    return state


async def test_run_updates_career_dna_and_hypotheses():
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    assert profile.career_dna.traits["curiosity"].score == 0.7
    assert len(profile.career_hypotheses) == 1
    assert profile.career_hypotheses[0].career_name == "AI Research"
    assert any(e.kind == "conversation" for e in profile.exploration_history)
    assert result["messages"][-1].content == BASE_ARGS["reply_to_student"]


async def test_career_dna_update_is_recorded_in_evidence_graph_and_notebook():
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    trait_evidence = [e for e in profile.evidence_graph if e.related_trait == "curiosity"]
    assert len(trait_evidence) == 1
    assert trait_evidence[0].text == "Said they love figuring out how things work"
    assert trait_evidence[0].relation == "supports"

    observations = [e for e in profile.notebook_entries if e.kind == "observation"]
    assert len(observations) == 1
    assert observations[0].related_trait == "curiosity"
    assert observations[0].text == "High curiosity"


async def test_repeated_identical_trait_summary_does_not_duplicate_notebook_entries():
    profile = StudentProfile(student_id="s1")
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    state["messages"] = [HumanMessage(content="turn 1")]
    llm1 = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = await DiscoveryAgent().run(state, llm=llm1)

    # Same trait, same score, same summary — the LLM re-stating unchanged info.
    state["messages"] = [HumanMessage(content="turn 2")]
    llm2 = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    result = await DiscoveryAgent().run(state, llm=llm2)

    profile = result["student_profile"]
    curiosity_observations = [
        e for e in profile.notebook_entries if e.kind == "observation" and e.related_trait == "curiosity"
    ]
    assert len(curiosity_observations) == 1
    curiosity_evidence = [e for e in profile.evidence_graph if e.related_trait == "curiosity"]
    assert len(curiosity_evidence) == 1


async def test_new_hypothesis_creates_investigating_status_and_belief_revision():
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    hypothesis = profile.career_hypotheses[0]
    assert hypothesis.status in ("investigating", "growing")  # confidence 0.3 -> growing
    assert hypothesis.transition_reason == "Aureon started testing a new idea."

    revisions = [e for e in profile.notebook_entries if e.kind == "belief_revision"]
    assert len(revisions) == 1
    assert "started testing a new idea" in revisions[0].text.lower()
    assert revisions[0].previous_state == "none"


async def test_hypothesis_confidence_increase_strengthens_and_records_revision():
    profile = StudentProfile(student_id="s1")
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    state["messages"] = [HumanMessage(content="turn 1")]
    llm1 = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = await DiscoveryAgent().run(state, llm=llm1)

    strengthened_args = {
        **BASE_ARGS,
        "hypotheses": [
            {
                "career_name": "AI Research",
                "confidence": 0.6,
                "supporting_evidence": ["curiosity", "loves debugging"],
                "missing_evidence": ["leadership"],
                "contradicting_evidence": [],
            }
        ],
    }
    state["messages"] = [HumanMessage(content="turn 2")]
    llm2 = FakeLLMClient([tool_call_response("record_discovery_turn", strengthened_args)])
    result = await DiscoveryAgent().run(state, llm=llm2)

    profile = result["student_profile"]
    hypothesis = profile.career_hypotheses[0]
    assert hypothesis.confidence == 0.6
    assert hypothesis.status == "strong"

    revisions = [e for e in profile.notebook_entries if e.kind == "belief_revision"]
    assert any("strengthened" in r.text.lower() for r in revisions)

    # New supporting evidence item is deduped against what's already there.
    supports = [
        e for e in profile.evidence_graph if e.related_hypothesis == "AI Research" and e.relation == "supports"
    ]
    assert {e.text for e in supports} == {"curiosity", "loves debugging"}


async def test_hypothesis_dropped_by_llm_is_discarded_not_deleted():
    profile = StudentProfile(student_id="s1")
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    state["messages"] = [HumanMessage(content="turn 1")]
    llm1 = FakeLLMClient([tool_call_response("record_discovery_turn", BASE_ARGS)])
    state = await DiscoveryAgent().run(state, llm=llm1)

    dropped_args = {**BASE_ARGS, "hypotheses": []}
    state["messages"] = [HumanMessage(content="turn 2")]
    llm2 = FakeLLMClient([tool_call_response("record_discovery_turn", dropped_args)])
    result = await DiscoveryAgent().run(state, llm=llm2)

    profile = result["student_profile"]
    assert len(profile.career_hypotheses) == 1  # kept, not deleted
    assert profile.career_hypotheses[0].status == "discarded"
    assert profile.career_hypotheses[0].transition_reason is not None

    revisions = [e for e in profile.notebook_entries if e.kind == "belief_revision"]
    assert any("set aside" in r.text.lower() for r in revisions)


async def test_contradicting_evidence_is_recorded_separately_from_supporting():
    args = {
        **BASE_ARGS,
        "hypotheses": [
            {
                "career_name": "AI Research",
                "confidence": 0.4,
                "supporting_evidence": ["enjoys research"],
                "missing_evidence": ["leadership"],
                "contradicting_evidence": ["said they dislike working alone"],
            }
        ],
    }
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    contradicts = [
        e for e in profile.evidence_graph if e.related_hypothesis == "AI Research" and e.relation == "contradicts"
    ]
    assert len(contradicts) == 1
    assert contradicts[0].text == "said they dislike working alone"


async def test_suggested_activity_requires_reason():
    args = {
        **BASE_ARGS,
        "suggested_activity": {
            "title": "Build a tiny tool",
            "description": "Spend 20 minutes building something small.",
            "reason": "Missing evidence on leadership for the AI Research hypothesis.",
        },
    }
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    payload = result["agent_outputs"]["discovery"].payload["suggested_activity"]
    assert payload["reason"] == "Missing evidence on leadership for the AI Research hypothesis."


async def test_confidence_is_bounded_by_deterministic_ceiling():
    args = {**BASE_ARGS, "confidence_score": 1.0}
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    # Only one evidence item this turn -> ceiling is far below 1.0 even
    # though the LLM claimed full confidence.
    assert result["confidence_score"] < 0.3
    assert result["mode"] == Mode.EXPLORATION.value


async def test_mode_switches_to_recommendation_once_evidence_and_confidence_are_high():
    profile = StudentProfile(student_id="s1")
    profile.exploration_history = [
        ExplorationEvent(kind="conversation", description=f"evidence {i}") for i in range(7)
    ]
    args = {**BASE_ARGS, "confidence_score": 0.9}
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    state["messages"] = [HumanMessage(content="hello")]

    result = await DiscoveryAgent().run(state, llm=llm)

    assert result["confidence_score"] >= 0.6
    assert result["mode"] == Mode.RECOMMENDATION.value


async def test_leading_hypothesis_reaches_validated_once_recommendation_mode_is_reached():
    profile = StudentProfile(student_id="s1")
    profile.exploration_history = [
        ExplorationEvent(kind="conversation", description=f"evidence {i}") for i in range(7)
    ]
    args = {**BASE_ARGS, "confidence_score": 0.9}
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = new_state(conversation_id="c1", student_id="s1", student_profile=profile)
    state["messages"] = [HumanMessage(content="hello")]

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    assert profile.career_hypotheses[0].status == "validated"


async def test_why_probe_depth_cap_overrides_llm_after_limit():
    args = {
        **BASE_ARGS,
        "probe": {"is_probing": True, "topic": "wants_to_be_doctor", "depth": WHY_PROBE_DEPTH_CAP + 1},
    }
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()
    state["why_probe_state"] = {"wants_to_be_doctor": WHY_PROBE_DEPTH_CAP}

    result = await DiscoveryAgent().run(state, llm=llm)

    # Code overrides the LLM's attempt to probe past the cap.
    assert result["agent_outputs"]["discovery"].payload["probe"]["is_probing"] is False
    assert result["why_probe_state"]["wants_to_be_doctor"] == WHY_PROBE_DEPTH_CAP


async def test_why_probe_allowed_under_cap():
    args = {
        **BASE_ARGS,
        "probe": {"is_probing": True, "topic": "wants_to_be_doctor", "depth": 1},
    }
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    assert result["agent_outputs"]["discovery"].payload["probe"]["is_probing"] is True
    assert result["why_probe_state"]["wants_to_be_doctor"] == 1


async def test_reflection_journal_records_answer_to_pending_prompt():
    args = {**BASE_ARGS, "reflection_prompt": None}
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message("It surprised me how much I enjoyed the debugging part")
    state["pending_reflection_prompt"] = "What surprised you about that activity?"

    result = await DiscoveryAgent().run(state, llm=llm)

    profile = result["student_profile"]
    assert len(profile.reflection_journal) == 1
    entry = profile.reflection_journal[0]
    assert entry.prompt == "What surprised you about that activity?"
    assert entry.response == "It surprised me how much I enjoyed the debugging part"
    assert entry.answered_at is not None
    assert any(e.kind == "reflection" for e in profile.exploration_history)
    assert result["pending_reflection_prompt"] is None


async def test_new_reflection_prompt_is_carried_forward_in_state():
    args = {**BASE_ARGS, "reflection_prompt": "What frustrated you today?"}
    llm = FakeLLMClient([tool_call_response("record_discovery_turn", args)])
    state = _state_with_message()

    result = await DiscoveryAgent().run(state, llm=llm)

    assert result["pending_reflection_prompt"] == "What frustrated you today?"
