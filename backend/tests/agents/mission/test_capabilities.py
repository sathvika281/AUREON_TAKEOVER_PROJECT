from aureon.agents.mission.capabilities import AGENT_CAPABILITIES, Capability, owns_capability
from aureon.shared.types import AgentName


#: Network/Portfolio are Phase 2 Foundation registration placeholders —
#: deliberately absent from AGENT_CAPABILITIES (owns_capability already
#: treats an absent key as "owns nothing," the most honest placeholder
#: state; see agents/specialized/network/agent.py, .../portfolio/agent.py).
_PLACEHOLDER_AGENTS = {AgentName.NETWORK.value, AgentName.PORTFOLIO.value}


def test_every_non_placeholder_agent_name_has_a_capability_mapping():
    for name in AgentName:
        if name.value in _PLACEHOLDER_AGENTS:
            assert name.value not in AGENT_CAPABILITIES
            continue
        assert name.value in AGENT_CAPABILITIES
        assert len(AGENT_CAPABILITIES[name.value]) > 0


def test_mentor_owns_investigation_and_knowledge_fusion_only():
    caps = AGENT_CAPABILITIES[AgentName.MENTOR.value]
    assert Capability.INVESTIGATION in caps
    assert Capability.KNOWLEDGE_FUSION in caps
    assert Capability.DOCUMENT_INTELLIGENCE not in caps


def test_institution_owns_document_intelligence():
    assert owns_capability(AgentName.INSTITUTION.value, Capability.DOCUMENT_INTELLIGENCE)
    assert not owns_capability(AgentName.INSTITUTION.value, Capability.DELEGATION)


def test_only_decision_and_career_orchestrator_own_delegation():
    # CareerOrchestratorAgent legitimately gained DELEGATION too — it
    # coordinates delegation across an entire Build Orchestrator plan,
    # the same real responsibility Decision already had for its own flows.
    owners = {name for name, caps in AGENT_CAPABILITIES.items() if Capability.DELEGATION in caps}
    assert owners == {AgentName.DECISION.value, AgentName.CAREER_ORCHESTRATOR.value}
