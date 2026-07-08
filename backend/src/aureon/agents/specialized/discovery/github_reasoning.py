from aureon.agents.specialized.discovery.github_evidence import ReasoningFacts, SkillFinding
from aureon.agents.specialized.discovery.github_prompts import build_github_investigation_messages
from aureon.agents.specialized.discovery.github_schemas import (
    GITHUB_INVESTIGATION_TOOL,
    GitHubInvestigationTurnOutput,
)
from aureon.services.llm.base import LLMClient


async def analyze_repository(
    facts: ReasoningFacts, skills: list[SkillFinding], *, llm: LLMClient
) -> GitHubInvestigationTurnOutput:
    """The single reasoning entry point for GitHub Intelligence — facts
    and skills are already fully real and deterministic (github_reader.py
    + github_evidence.py); this call only organizes them into an
    Engineering Intelligence Report, never inventing beyond what's given,
    and never seeing popularity metrics at all (see
    github_prompts.py::POPULARITY_EXCLUSION_RULE)."""
    def _insufficient(reason: str) -> GitHubInvestigationTurnOutput:
        return GitHubInvestigationTurnOutput(
            overall_summary="Could not analyze this repository this time.",
            project_purpose="", technical_complexity="", problem_solving="", code_organization="",
            technology_breadth="", documentation_quality="", learning_signals="",
            engineering_maturity="", research_orientation="", ai_ml_signals="",
            insufficient_content=True,
            insufficient_content_reason=reason,
        )

    messages = build_github_investigation_messages(facts=facts, skills=skills)
    try:
        response = await llm.complete(messages, tools=[GITHUB_INVESTIGATION_TOOL], tool_choice="required")
    except Exception:  # noqa: BLE001 — a provider-side error (e.g. malformed tool-call arguments)
        # must never crash the mission; it degrades to an honest,
        # unfabricated "couldn't analyze this time" result instead.
        return _insufficient("Investigation could not be completed this time.")

    if not response.tool_calls:
        return _insufficient("Investigation could not be completed this time.")

    try:
        return GitHubInvestigationTurnOutput.model_validate(response.tool_calls[0].arguments)
    except Exception:  # noqa: BLE001 — malformed arguments from the model are never trusted blindly
        return _insufficient("Investigation could not be completed this time.")
