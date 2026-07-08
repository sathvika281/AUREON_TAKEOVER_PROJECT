from aureon.agents.specialized.decision.simulation_alignment import AlignmentFacts
from aureon.agents.specialized.decision.simulation_prompts import (
    build_decision_insights_messages,
    build_simulation_messages,
)
from aureon.agents.specialized.decision.simulation_schemas import (
    DECISION_INSIGHTS_TOOL,
    SIMULATION_TOOL,
    CareerSimulationTurnOutput,
    DecisionInsightsTurnOutput,
)
from aureon.agents.specialized.growth.evidence_summary import ProgressEvidenceBundle
from aureon.domain.models.career import Career
from aureon.domain.models.career_dna import CareerDNA
from aureon.services.llm.base import LLMClient


def _insufficient_simulation(reason: str) -> CareerSimulationTurnOutput:
    return CareerSimulationTurnOutput(
        learning_journey="", insufficient_evidence=True, insufficient_evidence_reason=reason,
    )


async def analyze_career_simulation(
    career: Career,
    facts: dict[str, str],
    alignment: AlignmentFacts,
    *,
    career_dna: CareerDNA,
    progress: ProgressEvidenceBundle,
    llm: LLMClient,
) -> CareerSimulationTurnOutput:
    """One independent simulation call for a single career path — never
    sees any other candidate career, so its reasoning can't become
    relative/contrastive at the wrong stage (see analyze_decision_insights
    for where cross-career comparison genuinely belongs)."""
    messages = build_simulation_messages(
        career=career, facts=facts, alignment=alignment, career_dna=career_dna, progress=progress,
    )
    try:
        response = await llm.complete(messages, tools=[SIMULATION_TOOL], tool_choice="required")
    except Exception:  # noqa: BLE001 — a provider-side error must never crash the mission
        return _insufficient_simulation("This simulation could not be completed this time.")

    if not response.tool_calls:
        return _insufficient_simulation("This simulation could not be completed this time.")

    try:
        return CareerSimulationTurnOutput.model_validate(response.tool_calls[0].arguments)
    except Exception:  # noqa: BLE001 — malformed arguments from the model are never trusted blindly
        return _insufficient_simulation("This simulation could not be completed this time.")


def _insufficient_insights(reason: str) -> DecisionInsightsTurnOutput:
    return DecisionInsightsTurnOutput(insufficient_evidence=True, insufficient_evidence_reason=reason)


async def analyze_decision_insights(
    entries: list[tuple[str, str, CareerSimulationTurnOutput]], *, llm: LLMClient
) -> DecisionInsightsTurnOutput:
    """The one place cross-career comparison/contrast reasoning happens —
    reads only the already-generated independent simulations."""
    messages = build_decision_insights_messages(entries=entries)
    try:
        response = await llm.complete(messages, tools=[DECISION_INSIGHTS_TOOL], tool_choice="required")
    except Exception:  # noqa: BLE001 — a provider-side error must never crash the mission
        return _insufficient_insights("Decision insights could not be generated this time.")

    if not response.tool_calls:
        return _insufficient_insights("Decision insights could not be generated this time.")

    try:
        output = DecisionInsightsTurnOutput.model_validate(response.tool_calls[0].arguments)
    except Exception:  # noqa: BLE001 — malformed arguments from the model are never trusted blindly
        return _insufficient_insights("Decision insights could not be generated this time.")

    known_ids = {cid for cid, _, _ in entries}
    if output.strongest_match_career_id is not None and output.strongest_match_career_id not in known_ids:
        output.strongest_match_career_id = None
    return output
