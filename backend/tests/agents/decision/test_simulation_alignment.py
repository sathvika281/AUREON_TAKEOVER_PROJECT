from datetime import datetime, timezone

from aureon.agents.specialized.decision.simulation_alignment import compute_alignment
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.student_profile import StudentProfile

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)
CAREER = Career(
    id="ai_research", name="AI Research", category="research", industry="tech",
    trait_tags=["curiosity", "analytical"], one_liner="x", reality=_REALITY, future_lens=_FUTURE,
)


def _candidate(confidence: float = 0.7) -> CareerCandidate:
    return CareerCandidate(
        id="c1", career_id="ai_research", career_name="AI Research",
        why_it_matches="Strong alignment with your curiosity trait.", confidence=confidence,
    )


def test_career_dna_alignment_uses_real_candidate_reasoning():
    profile = StudentProfile(student_id="s1")
    alignment = compute_alignment(profile, CAREER, _candidate())
    assert "Strong alignment with your curiosity trait." in alignment.career_dna_alignment


def test_evidence_confidence_counts_real_supporting_and_contradicting_evidence():
    profile = StudentProfile(student_id="s1")
    now = datetime.now(timezone.utc)
    profile.evidence_graph.append(EvidenceRecord(
        id="e1", text="x", source="conversation", related_career="ai_research", relation="supports", created_at=now,
    ))
    profile.evidence_graph.append(EvidenceRecord(
        id="e2", text="x", source="conversation", related_career="ai_research", relation="supports", created_at=now,
    ))
    profile.evidence_graph.append(EvidenceRecord(
        id="e3", text="x", source="conversation", related_career="other_career", relation="supports", created_at=now,
    ))

    alignment = compute_alignment(profile, CAREER, _candidate())

    assert "2 supporting" in alignment.evidence_confidence
    assert "0 contradicting" in alignment.evidence_confidence


def test_student_interest_alignment_honest_when_no_interests_recorded():
    profile = StudentProfile(student_id="s1")
    alignment = compute_alignment(profile, CAREER, _candidate())
    assert alignment.student_interest_alignment == "No stated interests recorded yet."


def test_student_interest_alignment_detects_real_overlap():
    profile = StudentProfile(student_id="s1", interests=["curiosity", "cooking"])
    alignment = compute_alignment(profile, CAREER, _candidate())
    assert "curiosity" in alignment.student_interest_alignment
    assert "cooking" not in alignment.student_interest_alignment
