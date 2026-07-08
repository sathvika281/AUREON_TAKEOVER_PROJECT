from aureon.agents.specialized.career_intelligence.confidence import evidence_strength_label
from aureon.agents.specialized.discovery.hidden_potential import derive_hidden_potential
from aureon.agents.specialized.discovery.understanding_level import derive_understanding_level
from aureon.domain.models.student_profile import StudentProfile
from aureon.shared.schemas import (
    CareerCandidateDTO,
    CareerHypothesisDTO,
    EvidenceRecordDTO,
    HiddenPotentialPatternDTO,
    NotebookEntryDTO,
    TraitSignalDTO,
)

"""Shared presentation mapping from StudentProfile -> API DTOs, used by
both POST /conversation/turn and GET .../discovery-profile so the
evidence-filtering and derivation logic lives in exactly one place
rather than being duplicated across routes."""


def _hypothesis_evidence(profile: StudentProfile, career_name: str, relation: str) -> list[str]:
    return [
        e.text
        for e in profile.evidence_graph
        if e.related_hypothesis == career_name and e.relation == relation
    ]


def build_career_dna_dto(profile: StudentProfile) -> dict[str, TraitSignalDTO]:
    return {
        trait: TraitSignalDTO(score=signal.score, summary=signal.summary)
        for trait, signal in profile.career_dna.traits.items()
    }


def build_hypothesis_dtos(profile: StudentProfile) -> list[CareerHypothesisDTO]:
    """Discarded hypotheses are omitted here — the Working Hypotheses
    view only shows what's still live; the discard event itself already
    landed in the Notebook when it happened."""
    return [
        CareerHypothesisDTO(
            career_name=h.career_name,
            confidence=h.confidence,
            status=h.status,
            transition_reason=h.transition_reason,
            supporting_evidence=_hypothesis_evidence(profile, h.career_name, "supports"),
            contradicting_evidence=_hypothesis_evidence(profile, h.career_name, "contradicts"),
            missing_evidence=h.missing_evidence,
        )
        for h in profile.career_hypotheses
        if h.status != "discarded"
    ]


def build_hidden_potential_dtos(profile: StudentProfile) -> list[HiddenPotentialPatternDTO]:
    return [
        HiddenPotentialPatternDTO(
            id=p.id,
            trait_a=p.trait_a,
            trait_b=p.trait_b,
            sentence=p.sentence,
            supporting_evidence=p.supporting_evidence,
        )
        for p in derive_hidden_potential(profile.career_dna, profile.evidence_graph)
    ]


def build_understanding_level(profile: StudentProfile, *, mode: str) -> tuple[str, str]:
    has_hidden_potential = len(derive_hidden_potential(profile.career_dna, profile.evidence_graph)) > 0
    return derive_understanding_level(
        career_dna=profile.career_dna,
        hypotheses=profile.career_hypotheses,
        mode=mode,
        has_hidden_potential=has_hidden_potential,
    )


def build_notebook_entry_dtos(profile: StudentProfile) -> list[NotebookEntryDTO]:
    return [
        NotebookEntryDTO(
            id=e.id,
            kind=e.kind,
            text=e.text,
            source=e.source,
            related_trait=e.related_trait,
            related_hypothesis=e.related_hypothesis,
            related_career=e.related_career,
            confidence_label=e.confidence_label,
            previous_state=e.previous_state,
            new_evidence=e.new_evidence,
            updated_belief=e.updated_belief,
            reason=e.reason,
            created_at=e.created_at,
        )
        for e in profile.notebook_entries
    ]


def build_evidence_graph_dtos(profile: StudentProfile) -> list[EvidenceRecordDTO]:
    return [
        EvidenceRecordDTO(
            id=e.id,
            text=e.text,
            source=e.source,
            related_trait=e.related_trait,
            related_hypothesis=e.related_hypothesis,
            related_career=e.related_career,
            relation=e.relation,
            created_at=e.created_at,
        )
        for e in profile.evidence_graph
    ]


def _career_evidence(profile: StudentProfile, career_id: str, relation: str) -> list[str]:
    return [
        e.text
        for e in profile.evidence_graph
        if e.related_career == career_id and e.relation == relation
    ]


def build_career_candidate_dtos(profile: StudentProfile) -> list[CareerCandidateDTO]:
    """No raw confidence number is ever exposed — only the deterministic
    qualitative Evidence Strength label, same treatment as hypotheses.
    Discarded candidates are omitted here — the discard event itself
    already landed in the Notebook when it happened, same convention as
    ``build_hypothesis_dtos``."""
    return [
        CareerCandidateDTO(
            career_id=c.career_id,
            career_name=c.career_name,
            why_it_matches=c.why_it_matches,
            evidence_strength=evidence_strength_label(c.confidence),
            uncertainty_reason=c.uncertainty_reason,
            supporting_evidence=_career_evidence(profile, c.career_id, "supports"),
            contradicting_evidence=_career_evidence(profile, c.career_id, "contradicts"),
            missing_evidence=c.missing_evidence,
            is_shortlisted=c.is_shortlisted,
        )
        for c in profile.career_candidates
        if c.status != "discarded"
    ]
