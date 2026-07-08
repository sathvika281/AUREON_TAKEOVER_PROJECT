from enum import StrEnum

from aureon.shared.types import AgentName


class Capability(StrEnum):
    """The finite set of reasoning workflows a specialist may own. A
    specialist's presence in ``AGENT_CAPABILITIES`` below is a contract:
    it may only be delegated work that matches one of its own
    capabilities (enforced by ``MissionOrchestrator.delegate`` — see
    ``agents/mission/orchestrator.py``), and it should never reach into a
    capability owned by another specialist itself."""

    INVESTIGATION = "investigation"
    PLANNING = "planning"
    EXPERIMENT_DESIGN = "experiment_design"
    KNOWLEDGE_FUSION = "knowledge_fusion"
    TREND_MONITORING = "trend_monitoring"
    MEMORY_RECALL = "memory_recall"
    DELEGATION = "delegation"
    DOCUMENT_INTELLIGENCE = "document_intelligence"


#: Every specialist owns only what naturally belongs to it — deliberately
#: not a "give everyone everything" map. ``growth`` fulfills the spec's
#: "Progress Agent" role (see its docstring); ``skill_gap`` is a
#: pre-existing stub not named in the V4 spec's 8 agents, kept consistent
#: with a sensible minimal mapping rather than left undocumented.
AGENT_CAPABILITIES: dict[str, frozenset[Capability]] = {
    AgentName.DISCOVERY.value: frozenset({
        Capability.INVESTIGATION,
        Capability.EXPERIMENT_DESIGN,
        Capability.KNOWLEDGE_FUSION,
        Capability.MEMORY_RECALL,
    }),
    AgentName.CAREER_INTELLIGENCE.value: frozenset({
        Capability.INVESTIGATION,
        Capability.PLANNING,
        Capability.KNOWLEDGE_FUSION,
        Capability.TREND_MONITORING,
    }),
    AgentName.DECISION.value: frozenset({
        Capability.KNOWLEDGE_FUSION,
        Capability.DELEGATION,
        Capability.INVESTIGATION,
    }),
    AgentName.ROADMAP.value: frozenset({
        Capability.PLANNING,
        Capability.TREND_MONITORING,
    }),
    AgentName.OPPORTUNITY.value: frozenset({
        Capability.INVESTIGATION,
        Capability.TREND_MONITORING,
    }),
    AgentName.GROWTH.value: frozenset({
        Capability.MEMORY_RECALL,
        Capability.PLANNING,
    }),
    AgentName.INSTITUTION.value: frozenset({
        Capability.INVESTIGATION,
        Capability.DOCUMENT_INTELLIGENCE,
    }),
    AgentName.MENTOR.value: frozenset({
        Capability.INVESTIGATION,
        Capability.KNOWLEDGE_FUSION,
    }),
    AgentName.SKILL_GAP.value: frozenset({
        Capability.PLANNING,
        Capability.INVESTIGATION,
    }),
}


def owns_capability(agent_name: str, capability: Capability) -> bool:
    return capability in AGENT_CAPABILITIES.get(agent_name, frozenset())
