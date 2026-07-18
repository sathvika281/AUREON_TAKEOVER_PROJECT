"""Responsibility: Hidden Potential Service — the single canonical
backend source for everything related to strengths, potential, and
evidence progression. Composes (never rewrites) 4 existing pieces:
Hidden Potential Engine (agents/specialized/discovery/hidden_potential.py),
Talent Pattern Engine (talent_pattern_engine.py), Experiment History
Service (experiment_history.py), and Progressive Discovery's existing
suggested_experiment recommendation. None of those four files are
modified by this module — each is called exactly once. Consumed by:
api/v1/hidden_potential_routes.py.
"""

from aureon.agents.specialized.discovery.hidden_potential import derive_hidden_potential
from aureon.domain.models.experiment import Experiment
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.models.talent import TalentPattern
from aureon.domain.services.experiment_history import get_experiment_history
from aureon.domain.services.progressive_discovery import get_progressive_discovery_state
from aureon.domain.services.talent_pattern_engine import analyze_talents
from aureon.shared.schemas import (
    DiscoveryStatisticsDTO,
    EvidenceTimelineItemDTO,
    HiddenPotentialPatternDTO,
    HiddenPotentialResponse,
    StrengthsGroupDTO,
    TalentEvidenceItemDTO,
    TalentPatternDTO,
)

#: Same threshold already used client-side in HiddenPotentialScreen.tsx
#: (Discover Batch 1) — relocated here so discovery_statistics can be
#: computed server-side, not a newly invented value.
STRONG_EVIDENCE_THRESHOLD = 0.4


def _talent_pattern_dto(pattern: TalentPattern) -> TalentPatternDTO:
    return TalentPatternDTO(
        talent=pattern.talent,
        tier=pattern.tier,
        explanation=pattern.explanation,
        evidence=[
            TalentEvidenceItemDTO(source=e.source, description=e.description, observed_at=e.observed_at)
            for e in pattern.evidence
        ],
    )


def build_hidden_potential_response(
    profile: StudentProfile, *, experiments: list[Experiment]
) -> HiddenPotentialResponse:
    hidden_patterns = derive_hidden_potential(profile.career_dna, profile.evidence_graph)
    talent_patterns = analyze_talents(profile)

    #: Pure regrouping of analyze_talents' own already-computed tier field
    #: — zero new scoring/thresholds. still_discovering/emerging/growing
    #: are the real backend values; these are just this response's names.
    strengths = StrengthsGroupDTO(
        emerging=[_talent_pattern_dto(p) for p in talent_patterns if p.tier == "still_discovering"],
        growing=[_talent_pattern_dto(p) for p in talent_patterns if p.tier == "emerging"],
        consistently_observed=[_talent_pattern_dto(p) for p in talent_patterns if p.tier == "growing"],
    )

    #: Flattens each pattern's already-timestamped evidence into one
    #: sorted feed — no new evidence, no new timestamps.
    timeline = sorted(
        (
            EvidenceTimelineItemDTO(source=e.source, description=e.description, observed_at=e.observed_at, talent=p.talent)
            for p in talent_patterns
            for e in p.evidence
        ),
        key=lambda item: item.observed_at,
        reverse=True,
    )

    #: Reuses Progressive Discovery's exact existing suggested_experiment
    #: — calls the unmodified function, takes one field. No second
    #: recommendation engine; mode doesn't affect this field, so a fixed
    #: value is passed and every other field on the result is discarded.
    suggested_experience = get_progressive_discovery_state(
        profile, mode="exploration", experiments=experiments
    ).suggested_experiment

    strong_traits = [
        t for t in profile.career_dna.traits.values() if (t.score or 0) >= STRONG_EVIDENCE_THRESHOLD
    ]

    return HiddenPotentialResponse(
        hidden_patterns=[
            HiddenPotentialPatternDTO(
                id=p.id, trait_a=p.trait_a, trait_b=p.trait_b, sentence=p.sentence,
                supporting_evidence=p.supporting_evidence,
            )
            for p in hidden_patterns
        ],
        strengths=strengths,
        suggested_experience=suggested_experience,
        evidence_timeline=timeline,
        discovery_statistics=DiscoveryStatisticsDTO(
            traits_tracked=len(profile.career_dna.traits),
            traits_with_strong_evidence=len(strong_traits),
            hidden_patterns_found=len(hidden_patterns),
            strengths_found=len(talent_patterns),
            experiments_completed=len(get_experiment_history(profile)),
        ),
    )
