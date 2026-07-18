import aureon.agents.specialized  # noqa: F401  (registers every agent)
from aureon.agents.registry import AgentRegistry
from aureon.shared.types import AgentName


def test_all_agents_self_register():
    registered = set(AgentRegistry.names())
    expected = {name.value for name in AgentName}
    assert expected.issubset(registered)


def test_recommendation_stage_flags_match_confidence_gate_design():
    descriptors = {d.name: d for d in AgentRegistry.describe_all()}

    gated = {
        AgentName.CAREER_INTELLIGENCE.value,
        AgentName.DECISION.value,
        AgentName.ROADMAP.value,
    }
    for name in gated:
        assert descriptors[name].is_recommendation_stage is True

    ungated = {
        AgentName.DISCOVERY.value,
        AgentName.MENTOR.value,
        AgentName.SKILL_GAP.value,
        AgentName.INSTITUTION.value,
        AgentName.GROWTH.value,
    }
    for name in ungated:
        assert descriptors[name].is_recommendation_stage is False
