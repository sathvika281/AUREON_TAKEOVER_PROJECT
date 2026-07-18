"""Responsibility: Learning Style Evidence Builder — gathers real
evidence fragments per learning dimension from Career DNA (including the
existing qualitative "learning_style" trait), Experience Lab
completions, Reflection Journal, the Evidence Graph, and Hidden
Potential's Talent Pattern Engine (reused, called once, never
re-derived). Pure and stateless — no persistence, no LLM.
"""

from aureon.domain.models.experiment import Experiment, ExperimentCompletion
from aureon.domain.models.learning_style import LearningStyle, LearningStyleEvidenceItem
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentPattern

#: Real, natural mapping from Experience Lab's fixed experiment
#: categories onto the learning dimensions they most directly evidence.
CATEGORY_TO_DIMENSION_NAMES: dict[str, tuple[str, ...]] = {
    "read_abstract": ("Reading", "Analytical"),
    "debug_code": ("Practical", "Analytical"),
    "analyze_problem": ("Analytical", "Structured"),
    "observe_design": ("Visual", "Exploratory"),
    "reflect_on_workflow": ("Discussion-Based", "Independent"),
}

#: Real mapping from Talent Pattern Engine's fixed talent vocabulary
#: onto the learning dimensions a strong talent plausibly corroborates.
TALENT_TO_DIMENSION_NAMES: dict[str, tuple[str, ...]] = {
    "analytical_thinking": ("Analytical", "Structured"),
    "creativity": ("Exploratory", "Experimental"),
    "communication": ("Discussion-Based", "Collaborative"),
    "persistence": ("Independent", "Structured"),
    "empathy": ("Collaborative", "Discussion-Based"),
    "systems_thinking": ("Analytical", "Structured"),
}


def _matches(style: LearningStyle, text: str) -> bool:
    lowered = text.lower()
    tags = [k.lower() for k in (*style.keywords, style.name)]
    return any(tag in lowered or lowered in tag for tag in tags)


def _evidence_from_career_dna(style: LearningStyle, profile: StudentProfile) -> list[LearningStyleEvidenceItem]:
    items: list[LearningStyleEvidenceItem] = []
    learning_style_trait = profile.career_dna.traits.get("learning_style")
    if learning_style_trait and learning_style_trait.summary and _matches(style, learning_style_trait.summary):
        items.append(
            LearningStyleEvidenceItem(
                source="career_dna",
                description=f"Career DNA's own learning-style read: {learning_style_trait.summary}",
                observed_at=learning_style_trait.updated_at,
            )
        )
    for trait_name, signal in profile.career_dna.traits.items():
        if trait_name == "learning_style" or not signal.summary:
            continue
        if _matches(style, signal.summary):
            items.append(
                LearningStyleEvidenceItem(
                    source="career_dna",
                    description=f"Career DNA shows a real signal connected to {style.name.lower()} learning: {signal.summary}",
                    observed_at=signal.updated_at,
                )
            )
    return items


def _evidence_from_experiments(
    style: LearningStyle, completions: list[ExperimentCompletion], catalog_by_id: dict[str, Experiment]
) -> list[LearningStyleEvidenceItem]:
    """Looks up each completion's real category via the (caller-supplied)
    experiment catalog — ExperimentCompletion itself only denormalizes
    title/related_world/target_traits, not category, so this is the
    honest way to recover it rather than guessing from target_traits
    text."""
    items: list[LearningStyleEvidenceItem] = []
    for completion in completions:
        experiment = catalog_by_id.get(completion.experiment_id)
        if experiment is None:
            continue
        dimension_names = CATEGORY_TO_DIMENSION_NAMES.get(experiment.category, ())
        if style.name not in dimension_names:
            continue
        reported = [
            flag for flag in ("enjoyment", "curiosity", "persistence", "confidence") if getattr(completion.evidence, flag)
        ]
        description = f"Completed '{completion.experiment_title}', an activity naturally suited to {style.name.lower()} learning"
        if reported:
            description += f" — reported {', '.join(reported)}"
        items.append(LearningStyleEvidenceItem(source="experiment", description=description, observed_at=completion.completed_at))
    return items


def _evidence_from_reflections(style: LearningStyle, profile: StudentProfile) -> list[LearningStyleEvidenceItem]:
    items = []
    for entry in profile.reflection_journal:
        if not entry.response:
            continue
        if _matches(style, entry.response):
            items.append(
                LearningStyleEvidenceItem(
                    source="reflection",
                    description=f"A reflection response touched on {style.name.lower()} learning",
                    observed_at=entry.answered_at or entry.created_at,
                )
            )
    return items


def _evidence_from_evidence_graph(style: LearningStyle, profile: StudentProfile) -> list[LearningStyleEvidenceItem]:
    items = []
    for record in profile.evidence_graph:
        if _matches(style, record.text):
            items.append(
                LearningStyleEvidenceItem(
                    source="evidence_graph",
                    description=f"A conversation surfaced something connected to {style.name.lower()} learning: {record.text}",
                    observed_at=record.created_at,
                )
            )
    return items


def _evidence_from_talents(style: LearningStyle, talent_patterns: list[TalentPattern]) -> list[LearningStyleEvidenceItem]:
    items = []
    for pattern in talent_patterns:
        dimension_names = TALENT_TO_DIMENSION_NAMES.get(pattern.talent, ())
        if style.name not in dimension_names:
            continue
        latest = max((e.observed_at for e in pattern.evidence), default=None)
        if latest is None:
            continue
        items.append(
            LearningStyleEvidenceItem(
                source="hidden_potential",
                description=f"Hidden Potential has noticed real {pattern.talent.replace('_', ' ')}, which often pairs with {style.name.lower()} learning",
                observed_at=latest,
            )
        )
    return items


def build_evidence(
    style: LearningStyle,
    profile: StudentProfile,
    talent_patterns: list[TalentPattern],
    experiment_catalog: list[Experiment],
) -> list[LearningStyleEvidenceItem]:
    catalog_by_id = {e.id: e for e in experiment_catalog}
    evidence: list[LearningStyleEvidenceItem] = []
    evidence.extend(_evidence_from_career_dna(style, profile))
    evidence.extend(_evidence_from_experiments(style, profile.career_experiments, catalog_by_id))
    evidence.extend(_evidence_from_reflections(style, profile))
    evidence.extend(_evidence_from_evidence_graph(style, profile))
    evidence.extend(_evidence_from_talents(style, talent_patterns))
    return evidence
