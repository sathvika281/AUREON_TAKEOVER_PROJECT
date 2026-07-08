from aureon.agents.specialized.discovery.evidence.base import EvidenceSource
from aureon.agents.state import AureonState
from aureon.domain.models.student_profile import ExplorationEvent
from aureon.shared.types import AgentName


class ConversationEvidenceSource(EvidenceSource):
    """Formats this turn's LLM-extracted conversational evidence as
    ``ExplorationEvent``s. Does not call the LLM itself — Discovery
    Agent's single structured turn call already did the extraction; this
    source only exposes that result through the pluggable evidence
    interface so the aggregation step doesn't special-case "conversation"
    as different from any other source.
    """

    name = "conversation"
    description = "Evidence extracted directly from the student's conversation this turn."

    async def extract(self, state: AureonState) -> list[ExplorationEvent]:
        discovery_output = state["agent_outputs"].get(AgentName.DISCOVERY.value)
        if discovery_output is None:
            return []
        items = discovery_output.payload.get("extracted_evidence") or []
        return [
            ExplorationEvent(kind=item["kind"], description=item["description"])
            for item in items
        ]
