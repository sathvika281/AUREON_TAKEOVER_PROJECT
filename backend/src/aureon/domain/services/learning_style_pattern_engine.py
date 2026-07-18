"""Responsibility: Learning Style Pattern Engine — tiers each learning
dimension's real evidence into a qualitative confidence tier (never a
score), builds a grounded explanation, and surfaces real recommended
Experience Lab activities via a static category→dimension mapping
(reused catalog, zero duplicate scoring logic). Pure and stateless.
"""

from aureon.domain.models.experiment import Experiment
from aureon.domain.models.learning_style import LearningStyle, LearningStyleEvidenceItem, LearningStyleTier
from aureon.domain.services.learning_style_evidence import CATEGORY_TO_DIMENSION_NAMES

#: Same deterministic-ceiling philosophy as talent_pattern_engine.py.
_SOURCE_LABELS: dict[str, str] = {
    "career_dna": "Career DNA",
    "experiment": "Experience Lab",
    "reflection": "reflections",
    "evidence_graph": "conversations",
    "hidden_potential": "Hidden Potential",
}

#: Cap kept small and honest — never a wall of suggestions.
MAX_RECOMMENDED_EXPERIMENTS = 3


def tier_for(evidence: list[LearningStyleEvidenceItem]) -> LearningStyleTier | None:
    if not evidence:
        return None
    source_types = {item.source for item in evidence}
    if len(evidence) >= 3 and len(source_types) >= 2:
        return "strong"
    if len(evidence) >= 2:
        return "growing"
    return "still_emerging"


def build_explanation(style: LearningStyle, evidence: list[LearningStyleEvidenceItem], tier: LearningStyleTier) -> str:
    source_types = sorted({item.source for item in evidence}, key=list(_SOURCE_LABELS).index)
    source_phrase = " and ".join(_SOURCE_LABELS[s] for s in source_types)
    if tier == "strong":
        return f"Aureon has repeatedly observed {style.name.lower()} learning across your {source_phrase}."
    if tier == "growing":
        return f"Aureon has started to notice real signs of {style.name.lower()} learning in your {source_phrase}."
    return f"Aureon has noticed one early sign of {style.name.lower()} learning in your {source_phrase} — not enough yet to say much, but worth watching."


def recommended_experiments_for(
    style: LearningStyle, experiment_catalog: list[Experiment], completed_ids: set[str]
) -> list[Experiment]:
    matches = [
        e for e in experiment_catalog
        if e.id not in completed_ids and style.name in CATEGORY_TO_DIMENSION_NAMES.get(e.category, ())
    ]
    return matches[:MAX_RECOMMENDED_EXPERIMENTS]
