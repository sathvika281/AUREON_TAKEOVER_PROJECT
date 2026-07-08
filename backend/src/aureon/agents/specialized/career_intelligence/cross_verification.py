from pydantic import BaseModel, Field

from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.agents.tools.base import Evidence
from aureon.domain.models.career_investigation import InvestigationFinding
from aureon.services.llm.base import LLMClient
from aureon.services.llm.schemas import LLMMessage, LLMTool


class CareerInvestigationTurnOutput(BaseModel):
    """Structured contract for one Cross-Verification pass. Every
    ``InvestigationFinding`` must cite real evidence already collected —
    this call organizes/classifies agreement and disagreement across real
    sources, never inventing a claim beyond what's actually present in
    them."""

    overall_summary: str
    findings: list[InvestigationFinding] = Field(default_factory=list)
    agreements: list[str] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    #: Only ever set to one of the exact IDs the prompt was given — never
    #: a freshly invented career.
    related_career_id: str | None = None
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None


CROSS_VERIFICATION_TOOL = LLMTool(
    name="record_career_investigation",
    description="Record a cross-verified Career Investigation Report from real, already-collected evidence.",
    parameters=CareerInvestigationTurnOutput.model_json_schema(),
)


def _insufficient(reason: str) -> CareerInvestigationTurnOutput:
    return CareerInvestigationTurnOutput(
        overall_summary="Could not complete this investigation this time.",
        insufficient_evidence=True,
        insufficient_evidence_reason=reason,
    )


def _evidence_block(evidence: list[Evidence]) -> str:
    lines = []
    for i, e in enumerate(evidence, start=1):
        lines.append(f"{i}. [{e.source_type or 'unknown'}] {e.title or e.source}: {e.summary}")
    return "\n".join(lines)


def build_cross_verification_messages(
    *, question: str, evidence: list[Evidence], known_candidates: list[tuple[str, str]]
) -> list[LLMMessage]:
    candidates_block = (
        "\n".join(f"- {cid}: {name}" for cid, name in known_candidates)
        if known_candidates
        else "(the student has no tracked career candidates yet)"
    )
    system = (
        "You are Aureon's Career Intelligence Agent, cross-verifying real evidence gathered from "
        "multiple trusted sources to answer a student's career question — acting as a research "
        "analyst, not a chatbot.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "The evidence below was extracted directly from real sources — it is the ONLY source of "
        "truth you have. For each real claim you can support, classify it as 'supported' (sources "
        "agree), 'contradicted' (sources disagree), 'mixed' (partial agreement), or "
        "'insufficient_evidence' (not enough real evidence to say). Every finding must cite which "
        "of the numbered evidence items it draws from. Never present uncertain information as "
        "fact, and never invent a claim the evidence doesn't actually support.\n\n"
        "If you determine the evidence relates to one of the student's existing tracked career "
        "candidates below, set related_career_id to its EXACT id — never invent a new one, and "
        "leave it null if none clearly apply.\n\n"
        f"Known candidates:\n{candidates_block}\n\n"
        "If the evidence collected is too thin or off-topic to responsibly answer the question, "
        "set insufficient_evidence to true and explain why, rather than filling gaps with "
        "plausible-sounding guesses. Always respond by calling the record_career_investigation "
        "tool."
    )
    context = f"Student's question: {question}\n\nCollected evidence:\n{_evidence_block(evidence)}"
    return [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user", content=context),
    ]


async def analyze_evidence(
    question: str,
    evidence: list[Evidence],
    *,
    known_candidates: list[tuple[str, str]],
    llm: LLMClient,
) -> CareerInvestigationTurnOutput:
    messages = build_cross_verification_messages(question=question, evidence=evidence, known_candidates=known_candidates)
    try:
        response = await llm.complete(messages, tools=[CROSS_VERIFICATION_TOOL], tool_choice="required")
    except Exception:  # noqa: BLE001 — a provider-side error must never crash the mission
        return _insufficient("Investigation could not be completed this time.")

    if not response.tool_calls:
        return _insufficient("Investigation could not be completed this time.")

    try:
        output = CareerInvestigationTurnOutput.model_validate(response.tool_calls[0].arguments)
    except Exception:  # noqa: BLE001 — malformed arguments from the model are never trusted blindly
        return _insufficient("Investigation could not be completed this time.")

    known_ids = {cid for cid, _ in known_candidates}
    if output.related_career_id is not None and output.related_career_id not in known_ids:
        output.related_career_id = None
    return output
