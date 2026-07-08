from aureon.agents.specialized.discovery.evidence.base import EvidenceSource
from aureon.agents.state import AureonState
from aureon.domain.models.student_profile import ExplorationEvent
from aureon.shared.types import AgentName


class ReflectionEvidenceSource(EvidenceSource):
    """Formats a just-answered Reflection Journal entry as an
    ``ExplorationEvent``. Only produces evidence on the turn where the
    student actually answers a pending reflection prompt from the
    previous turn — otherwise contributes nothing.
    """

    name = "reflection"
    description = "Evidence from the student's answer to a pending reflection prompt."

    async def extract(self, state: AureonState) -> list[ExplorationEvent]:
        discovery_output = state["agent_outputs"].get(AgentName.DISCOVERY.value)
        if discovery_output is None:
            return []
        answered = discovery_output.payload.get("answered_reflection")
        if not answered:
            return []
        return [
            ExplorationEvent(
                kind="reflection",
                description=f"Reflected on \"{answered['prompt']}\": {answered['response']}",
            )
        ]
