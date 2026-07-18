"""Responsibility: Talent Analysis Service + Talent Pattern Engine (one
cohesive module — a separate orchestration wrapper around
``analyze_talents`` would be a pure pass-through). Reads real,
already-persisted evidence — Career DNA, Career Experiments, Reflection
Journal — and derives which talents are showing up, with a real,
evidence-citing explanation. Pure and stateless: recomputed on every
call, nothing persisted, same philosophy as
agents/specialized/discovery/hidden_potential.py and
domain/services/orbit_status.py. Never claims certainty and never
produces a numeric score — only three hedged tiers, each requiring real
evidence to reach.
"""

from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.experiment import ExperimentCompletion
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentEvidenceItem, TalentPattern, TalentTier

TALENT_NAMES = ("analytical_thinking", "creativity", "communication", "persistence", "empathy", "systems_thinking")

#: Same deterministic-ceiling philosophy as agents/specialized/career_intelligence/confidence.py
#: and world_signal.py's REINFORCE_STEP — a real trait score has to clear
#: this bar to count as evidence, not just be present.
STRONG_TRAIT_THRESHOLD = 0.5

#: A small, honest heuristic classifier over real reflection text — same
#: keyword-match discipline already used elsewhere in this codebase for
#: turning free text into a structured signal without an LLM call.
_REFLECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "analytical_thinking": ("figure out", "figured out", "understand why", "logic", "pattern", "solve", "solved"),
    "creativity": ("imagine", "idea", "design", "creative", "different way", "came up with"),
    "communication": ("explain", "explained", "shared", "talked", "wrote", "presented", "told"),
    "persistence": ("kept trying", "didn't give up", "difficult but", "eventually", "tried again", "kept going"),
    "empathy": ("felt for", "understood how", "perspective", "cared about", "how they felt"),
    "systems_thinking": ("connected", "whole picture", "how it all fits", "affects", "big picture"),
}

_TALENT_LABELS: dict[str, str] = {
    "analytical_thinking": "analytical thinking",
    "creativity": "creativity",
    "communication": "communication",
    "persistence": "persistence",
    "empathy": "empathy",
    "systems_thinking": "systems thinking",
}


def _evidence_from_career_dna(talent: str, career_dna: CareerDNA) -> TalentEvidenceItem | None:
    signal = career_dna.traits.get(talent)
    if signal is None or signal.score is None or signal.score < STRONG_TRAIT_THRESHOLD:
        return None
    description = f"Career DNA shows a real signal for {_TALENT_LABELS[talent]}"
    if signal.summary:
        description += f": {signal.summary}"
    return TalentEvidenceItem(source="career_dna", description=description, observed_at=signal.updated_at)


def _evidence_from_experiments(talent: str, completions: list[ExperimentCompletion]) -> list[TalentEvidenceItem]:
    items: list[TalentEvidenceItem] = []
    for completion in completions:
        if talent not in completion.target_traits:
            continue
        reported = [
            flag
            for flag in ("enjoyment", "curiosity", "persistence", "confidence")
            if getattr(completion.evidence, flag)
        ]
        description = f"Completed '{completion.experiment_title}', an experiment designed to surface {_TALENT_LABELS[talent]}"
        if reported:
            description += f" — reported {', '.join(reported)}"
        items.append(TalentEvidenceItem(source="experiment", description=description, observed_at=completion.completed_at))
    return items


def _evidence_from_reflections(talent: str, reflection_journal: list[ReflectionEntry]) -> list[TalentEvidenceItem]:
    keywords = _REFLECTION_KEYWORDS.get(talent, ())
    items: list[TalentEvidenceItem] = []
    for entry in reflection_journal:
        if not entry.response:
            continue
        lowered = entry.response.lower()
        if any(keyword in lowered for keyword in keywords):
            items.append(
                TalentEvidenceItem(
                    source="reflection",
                    description=f"A reflection response touched on {_TALENT_LABELS[talent]}",
                    observed_at=entry.answered_at or entry.created_at,
                )
            )
    return items


def _tier_for(evidence: list[TalentEvidenceItem]) -> TalentTier | None:
    if not evidence:
        return None
    source_types = {item.source for item in evidence}
    if len(evidence) >= 3 and len(source_types) >= 2:
        return "growing"
    if len(evidence) >= 2:
        return "emerging"
    return "still_discovering"


_SOURCE_LABELS: dict[str, str] = {
    "career_dna": "Career DNA",
    "experiment": "recent experiments",
    "reflection": "reflections",
}


def _build_explanation(talent: str, evidence: list[TalentEvidenceItem], tier: TalentTier) -> str:
    label = _TALENT_LABELS[talent]
    source_types = sorted({item.source for item in evidence}, key=list(_SOURCE_LABELS).index)
    source_phrase = " and ".join(_SOURCE_LABELS[s] for s in source_types)
    if tier == "growing":
        return f"Aureon has repeatedly observed strong {label} across your {source_phrase}."
    if tier == "emerging":
        return f"Aureon has started to notice real signs of {label} in your {source_phrase}."
    return f"Aureon has noticed one early sign of {label} in your {source_phrase} — not enough yet to say much, but worth watching."


def analyze_talents(profile: StudentProfile) -> list[TalentPattern]:
    patterns: list[TalentPattern] = []
    for talent in TALENT_NAMES:
        evidence: list[TalentEvidenceItem] = []
        dna_evidence = _evidence_from_career_dna(talent, profile.career_dna)
        if dna_evidence is not None:
            evidence.append(dna_evidence)
        evidence.extend(_evidence_from_experiments(talent, profile.career_experiments))
        evidence.extend(_evidence_from_reflections(talent, profile.reflection_journal))

        tier = _tier_for(evidence)
        if tier is None:
            continue
        patterns.append(
            TalentPattern(talent=talent, tier=tier, explanation=_build_explanation(talent, evidence, tier), evidence=evidence)
        )
    return patterns
