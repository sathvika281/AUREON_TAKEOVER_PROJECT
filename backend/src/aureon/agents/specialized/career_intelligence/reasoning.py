from aureon.agents.specialized.career_intelligence.prompts import build_career_intelligence_messages
from aureon.agents.specialized.career_intelligence.schemas import (
    CAREER_INTELLIGENCE_TOOL,
    CareerIntelligenceTurnOutput,
)
from aureon.domain.models.career import Career
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.llm.base import LLMClient


async def analyze_careers(
    profile: StudentProfile, careers: list[Career], *, llm: LLMClient
) -> CareerIntelligenceTurnOutput:
    """The single reasoning entry point for Career Intelligence — called
    both by the conversational agent (``agent.py``, planner-routed) and
    the direct analyze API route, so the reasoning logic lives in exactly
    one place regardless of how it was triggered."""
    messages = build_career_intelligence_messages(
        career_dna=profile.career_dna,
        hypotheses=profile.career_hypotheses,
        evidence_graph=profile.evidence_graph,
        careers=careers,
    )
    response = await llm.complete(
        messages, tools=[CAREER_INTELLIGENCE_TOOL], tool_choice="required"
    )
    return _parse_output(response)


def _parse_output(response) -> CareerIntelligenceTurnOutput:
    if not response.tool_calls:
        # Defensive fallback: never fabricate candidates when the model
        # didn't return structured output.
        return CareerIntelligenceTurnOutput(
            reply_to_student=response.content or "Let's gather a bit more evidence before exploring careers.",
            candidates=[],
            insufficient_evidence=True,
            insufficient_evidence_reason="Analysis could not be completed this time.",
        )
    return CareerIntelligenceTurnOutput.model_validate(response.tool_calls[0].arguments)
