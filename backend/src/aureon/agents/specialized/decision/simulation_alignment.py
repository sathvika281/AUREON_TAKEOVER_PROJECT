from dataclasses import dataclass

from aureon.agents.specialized.decision.confidence import (
    compute_candidate_confidence,
    evidence_strength_label,
)
from aureon.domain.models.career import Career
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.student_profile import StudentProfile


@dataclass
class AlignmentFacts:
    """The 3 student-alignment dimensions — deterministic, never LLM
    self-assessment. Same anti-fabrication discipline as V9's popularity
    exclusion and V10's source-availability exclusion: these are computed
    outside any LLM call and merged in afterward."""

    career_dna_alignment: str
    student_interest_alignment: str
    evidence_confidence: str


def _interest_overlap(profile: StudentProfile, career: Career) -> str:
    if not profile.interests:
        return "No stated interests recorded yet."

    career_terms = {career.name.lower(), career.category.lower(), *(t.lower() for t in career.trait_tags)}
    matched = [
        interest for interest in profile.interests
        if any(interest.lower() in term or term in interest.lower() for term in career_terms)
    ]
    if matched:
        return f"Overlaps with your stated interests: {', '.join(matched)}."
    return "No overlap detected yet between your stated interests and this career."


def compute_alignment(
    profile: StudentProfile, career: Career, candidate: CareerCandidate
) -> AlignmentFacts:
    """Deterministic facts only — reuses the exact same confidence-capping
    and evidence-strength-labeling utilities Career Candidates and
    Mentor/College Matches already use. Never touches the LLM."""
    supporting = sum(
        1 for e in profile.evidence_graph
        if e.related_career == career.id and e.relation == "supports"
    )
    contradicting = sum(
        1 for e in profile.evidence_graph
        if e.related_career == career.id and e.relation == "contradicts"
    )
    evidence_confidence = compute_candidate_confidence(candidate.confidence, supporting, contradicting)

    return AlignmentFacts(
        career_dna_alignment=(
            f"{evidence_strength_label(candidate.confidence)} — {candidate.why_it_matches}"
        ),
        student_interest_alignment=_interest_overlap(profile, career),
        evidence_confidence=(
            f"{evidence_strength_label(evidence_confidence)} "
            f"({supporting} supporting, {contradicting} contradicting evidence entries)"
        ),
    )
