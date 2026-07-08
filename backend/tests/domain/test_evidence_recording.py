from datetime import datetime, timezone

from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence

NOW = datetime.now(timezone.utc)


def test_records_new_evidence_for_a_hypothesis():
    profile = StudentProfile(student_id="s1")
    record_new_evidence(
        profile, related_hypothesis="AI Research", items=["enjoys research"],
        relation="supports", now=NOW,
    )
    assert len(profile.evidence_graph) == 1
    assert profile.evidence_graph[0].related_hypothesis == "AI Research"
    assert profile.evidence_graph[0].related_career is None


def test_records_new_evidence_for_a_career_candidate():
    profile = StudentProfile(student_id="s1")
    record_new_evidence(
        profile, related_career="ux_researcher", items=["enjoys studying user behavior"],
        relation="supports", now=NOW,
    )
    assert len(profile.evidence_graph) == 1
    assert profile.evidence_graph[0].related_career == "ux_researcher"
    assert profile.evidence_graph[0].related_hypothesis is None


def test_does_not_duplicate_already_recorded_text_for_the_same_subject():
    profile = StudentProfile(student_id="s1")
    record_new_evidence(
        profile, related_career="ux_researcher", items=["enjoys studying user behavior"],
        relation="supports", now=NOW,
    )
    record_new_evidence(
        profile, related_career="ux_researcher", items=["enjoys studying user behavior"],
        relation="supports", now=NOW,
    )
    assert len(profile.evidence_graph) == 1


def test_same_text_for_different_subjects_is_not_deduped_against_each_other():
    profile = StudentProfile(student_id="s1")
    record_new_evidence(
        profile, related_career="ux_researcher", items=["enjoys analyzing patterns"],
        relation="supports", now=NOW,
    )
    record_new_evidence(
        profile, related_career="civil_engineer", items=["enjoys analyzing patterns"],
        relation="supports", now=NOW,
    )
    assert len(profile.evidence_graph) == 2
