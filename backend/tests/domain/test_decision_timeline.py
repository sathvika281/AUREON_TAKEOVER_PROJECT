from datetime import datetime, timezone

from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_comparison import CareerComparison, ComparisonDimension
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.decision_timeline import build_decision_timeline

NOW = datetime.now(timezone.utc)


def test_empty_profile_produces_empty_timeline_and_no_fabricated_direction():
    profile = StudentProfile(student_id="s1")

    timeline = build_decision_timeline(profile)

    assert timeline.milestones == []
    assert "no clear direction" in timeline.current_direction_summary.lower()


def test_milestones_are_assembled_from_real_stored_data_only():
    profile = StudentProfile(student_id="s1")
    profile.notebook_entries.append(
        NotebookEntry(id="1", kind="observation", text="Noticed curiosity", source="conversation", created_at=NOW)
    )
    profile.notebook_entries.append(
        NotebookEntry(id="2", kind="belief_revision", text="Hypothesis strengthened", source="conversation",
                      related_hypothesis="AI Research", created_at=NOW)
    )
    profile.notebook_entries.append(
        NotebookEntry(id="3", kind="belief_revision", text="Candidate considered", source="conversation",
                      related_career="ai_research", created_at=NOW)
    )
    profile.career_comparisons.append(
        CareerComparison(
            id="c1", career_ids=["ai_research", "ux_research"],
            career_names={"ai_research": "AI Research", "ux_research": "UX Research"},
            dimensions=[ComparisonDimension(dimension="creativity", per_career={}, why_it_matters_to_you="x")],
            summary_reason="x", created_at=NOW,
        )
    )

    timeline = build_decision_timeline(profile)

    kinds = {m.kind for m in timeline.milestones}
    assert kinds == {"career_dna_change", "hypothesis_update", "career_candidate", "comparison"}
    assert len(timeline.milestones) == 4


def test_current_direction_prefers_shortlisted_candidate():
    profile = StudentProfile(student_id="s1")
    profile.career_candidates.append(
        CareerCandidate(id="1", career_id="ai_research", career_name="AI Research", why_it_matches="x", confidence=0.5, is_shortlisted=True)
    )
    profile.career_candidates.append(
        CareerCandidate(id="2", career_id="ux_research", career_name="UX Research", why_it_matches="x", confidence=0.9)
    )

    timeline = build_decision_timeline(profile)

    assert "AI Research" in timeline.current_direction_summary


def test_discarded_candidates_never_drive_current_direction():
    profile = StudentProfile(student_id="s1")
    profile.career_candidates.append(
        CareerCandidate(id="1", career_id="old", career_name="Old Career", why_it_matches="x", confidence=0.9, status="discarded")
    )

    timeline = build_decision_timeline(profile)

    assert "no clear direction" in timeline.current_direction_summary.lower()
