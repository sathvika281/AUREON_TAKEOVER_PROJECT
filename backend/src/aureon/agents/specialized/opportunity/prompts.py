"""Responsibility: the narrative LLM call's prompt construction — the
one place raw scoring facts are turned into the messages sent to the
model. Owns: `build_opportunity_narrative_messages`. Does NOT own: the
facts themselves (scoring.py/cost.py/journey.py) or the tool schema
(schemas.py). Consumed by: `agent.py`'s `find_opportunities`.

Mirrors `mentor/prompts.py`'s exact shape: a system message stating
`REASONING_DISCIPLINE` plus an explicit "facts only" instruction, and a
context block built entirely from already-computed facts — the model
never receives raw profile data, so it cannot invent anything about a
requirement, skill, deadline, or evidence item.
"""

from aureon.agents.mission.reasoning_discipline import REASONING_DISCIPLINE
from aureon.domain.models.opportunity import Opportunity
from aureon.domain.models.opportunity_fit import OpportunityFitResult
from aureon.services.llm.schemas import LLMMessage


def _opportunity_facts_block(opportunity: Opportunity, fit: OpportunityFitResult) -> str:
    lines = [
        f"Opportunity id={opportunity.id}: {opportunity.title} ({opportunity.category}, {opportunity.organization})",
        f"Overall fit score: {fit.overall_score:.2f} ({fit.readiness_label}); "
        f"requirements met: {fit.requirements_met} of {fit.requirements_total}.",
    ]
    for factor in fit.factors:
        lines.append(f"- {factor.label}: score={factor.score:.2f}, rationale={factor.rationale!r}")
    if fit.highest_impact_gap is not None:
        lines.append(
            f"Highest-impact gap: {fit.highest_impact_gap.label} — {fit.highest_impact_gap.recommended_action}"
        )
    if fit.strengths:
        lines.append(f"Strengths: {'; '.join(fit.strengths)}")
    if fit.gaps:
        lines.append(f"Gaps: {'; '.join(fit.gaps)}")
    lines.append(f"Why now: {fit.timing_rationale}")
    lines.append(f"If ignored: {fit.consequence_if_ignored}")
    return "\n".join(lines)


def build_opportunity_narrative_messages(
    recommendations: list[tuple[Opportunity, OpportunityFitResult]],
) -> list[LLMMessage]:
    system = (
        "You are Aureon's Opportunity Agent, explaining already-computed opportunity fit results to a "
        "student.\n\n"
        f"{REASONING_DISCIPLINE}\n\n"
        "You are given ONLY already-computed facts below for each opportunity — never invent a "
        "requirement, skill, deadline, or evidence item not present in these facts. Ground "
        "why_recommended in the student's real career-alignment evidence and stated goals where present, "
        "not just 'you have matching skills.' recommended_preparation should name the single "
        "highest-impact gap when one is given, not a generic list of every gap.\n\n"
        "Always respond by calling the record_opportunity_narratives tool, with exactly one narrative "
        "entry per opportunity_id given below."
    )
    context = "\n\n".join(_opportunity_facts_block(o, f) for o, f in recommendations)
    return [
        LLMMessage(role="system", content=system + "\n\n" + context),
        LLMMessage(role="user", content="Why were these opportunities recommended, and what should I prepare?"),
    ]
