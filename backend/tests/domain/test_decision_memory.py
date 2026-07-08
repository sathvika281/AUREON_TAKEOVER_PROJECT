from datetime import datetime, timezone

from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_comparison import CareerComparison, ComparisonDimension
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.decision_memory import (
    record_comparison_memory,
    remove_candidate,
    shortlist_candidate,
)

NOW = datetime.now(timezone.utc)


def test_comparison_memory_reuses_the_comparisons_own_summary_reason():
    profile = StudentProfile(student_id="s1")
    comparison = CareerComparison(
        id="c1", career_ids=["ai_research", "ux_research"],
        career_names={"ai_research": "AI Research", "ux_research": "UX Research"},
        dimensions=[ComparisonDimension(dimension="creativity", per_career={}, why_it_matters_to_you="x")],
        summary_reason="Preferred research-oriented work.", created_at=NOW,
    )

    entry = record_comparison_memory(profile, comparison, NOW)

    assert entry.action_type == "compared"
    assert entry.reason == "Preferred research-oriented work."
    assert profile.decision_memory[0] is entry


def test_shortlist_reason_is_derived_from_evidence_strength_not_a_new_call():
    profile = StudentProfile(student_id="s1")
    candidate = CareerCandidate(
        id="1", career_id="ai_research", career_name="AI Research",
        why_it_matches="x", confidence=0.9,  # -> "Strong" evidence strength
    )

    entry = shortlist_candidate(profile, candidate, NOW)

    assert candidate.is_shortlisted is True
    assert "Strong" in entry.reason
    assert entry.action_type == "shortlisted"


def test_remove_reason_is_derived_from_missing_evidence():
    profile = StudentProfile(student_id="s1")
    candidate = CareerCandidate(
        id="1", career_id="product_management", career_name="Product Management",
        why_it_matches="x", confidence=0.3, missing_evidence=["stakeholder-focused work experience"],
    )

    entry = remove_candidate(profile, candidate, NOW)

    assert candidate.status == "discarded"
    assert "stakeholder-focused work experience" in entry.reason
    assert entry.action_type == "removed"


def test_remove_with_no_missing_evidence_still_produces_a_reason():
    profile = StudentProfile(student_id="s1")
    candidate = CareerCandidate(id="1", career_id="x", career_name="X", why_it_matches="x", confidence=0.3)

    entry = remove_candidate(profile, candidate, NOW)

    assert entry.reason  # never empty/fabricated-looking
