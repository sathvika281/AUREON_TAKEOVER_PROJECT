from aureon.agents.mission.capabilities import AGENT_CAPABILITIES, Capability, owns_capability
from aureon.shared.types import AgentName


def test_every_agent_name_has_a_capability_mapping():
    for name in AgentName:
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


def test_only_decision_owns_delegation():
    owners = [name for name, caps in AGENT_CAPABILITIES.items() if Capability.DELEGATION in caps]
    assert owners == [AgentName.DECISION.value]
