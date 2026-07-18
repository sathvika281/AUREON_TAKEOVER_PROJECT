"""Responsibility: the 6 comparison dimensions Decide Batch 1 adds on
top of Decision Lab's existing 15 (`comparison_facts.py`) — Leadership,
Opportunity availability, Interest/Career DNA/Learning style/Mission
alignment. Built purely from already-computed `CareerDecisionCard`
fields; calls zero LLMs and re-analyzes nothing. Owns:
`build_extra_comparison_dimensions`. Consumed by:
`api/v1/decision.py`'s `POST /career-comparisons`, which appends the
result to a `CareerComparison.dimensions` list already finalized by the
existing, untouched LLM-reasoned flow.
"""

from aureon.domain.models.career import Career
from aureon.domain.models.career_comparison import ComparisonDimension
from aureon.domain.services.decision_workspace_service import CareerDecisionCard

EXTRA_COMPARISON_DIMENSIONS = [
    "leadership_emphasis",
    "opportunity_availability",
    "interest_alignment",
    "career_dna_alignment",
    "learning_style_alignment",
    "mission_alignment",
]

_WHY_IT_MATTERS: dict[str, str] = {
    "leadership_emphasis": "How much leadership responsibility this field typically involves.",
    "opportunity_availability": "How many real, matched opportunities Aureon has already found for this career.",
    "interest_alignment": "Whether your own real, observed interests connect to this field.",
    "career_dna_alignment": "How strong the evidence is that this career fits your Career DNA.",
    "learning_style_alignment": "Whether your dominant learning style pattern connects to this field's demands.",
    "mission_alignment": "Whether a real-world impact mission you resonate with connects to this field.",
}


def _leadership_fact(career: Career) -> str:
    if "leadership" in {t.lower() for t in career.trait_tags}:
        return "Yes — this field commonly involves leadership responsibility."
    return "Not typically emphasized in this field."


def _opportunity_fact(card: CareerDecisionCard) -> str:
    if not card.top_opportunities:
        return "No matched opportunities found yet."
    count = len(card.top_opportunities)
    return f"{count} real, matched {'opportunity' if count == 1 else 'opportunities'} found."


def _interest_fact(card: CareerDecisionCard) -> str:
    if not card.relevant_interests:
        return "No real interest signal observed yet."
    top = card.relevant_interests[0]
    count = len(top.evidence)
    return f"Real interest observed: {top.topic} ({count} {'piece' if count == 1 else 'pieces'} of evidence)."


def _career_dna_fact(card: CareerDecisionCard) -> str:
    return card.confidence_band


def _learning_style_fact(card: CareerDecisionCard) -> str:
    if card.learning_style_pattern is None:
        return "No matching learning style pattern yet."
    pattern = card.learning_style_pattern
    return f"{pattern.style.name} ({pattern.tier.replace('_', ' ')})."


def _mission_fact(card: CareerDecisionCard) -> str:
    if not card.related_life_missions:
        return "No related life mission signal yet."
    top = card.related_life_missions[0]
    return f"{top.mission.name} ({top.tier.replace('_', ' ')})."


def build_extra_comparison_dimensions(
    careers: list[Career], cards_by_career_id: dict[str, CareerDecisionCard]
) -> list[ComparisonDimension]:
    facts_by_dimension: dict[str, dict[str, str]] = {dim: {} for dim in EXTRA_COMPARISON_DIMENSIONS}

    for career in careers:
        card = cards_by_career_id.get(career.id)
        if card is None:
            continue
        facts_by_dimension["leadership_emphasis"][career.id] = _leadership_fact(career)
        facts_by_dimension["opportunity_availability"][career.id] = _opportunity_fact(card)
        facts_by_dimension["interest_alignment"][career.id] = _interest_fact(card)
        facts_by_dimension["career_dna_alignment"][career.id] = _career_dna_fact(card)
        facts_by_dimension["learning_style_alignment"][career.id] = _learning_style_fact(card)
        facts_by_dimension["mission_alignment"][career.id] = _mission_fact(card)

    return [
        ComparisonDimension(
            dimension=dim, per_career=facts_by_dimension[dim], why_it_matters_to_you=_WHY_IT_MATTERS[dim],
        )
        for dim in EXTRA_COMPARISON_DIMENSIONS
    ]
