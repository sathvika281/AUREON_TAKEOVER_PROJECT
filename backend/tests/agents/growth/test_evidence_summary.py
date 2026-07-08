from datetime import datetime, timedelta, timezone

from aureon.agents.specialized.growth.evidence_summary import (
    MIN_EVIDENCE_FOR_PROGRESS_REPORT,
    assemble_progress_evidence,
)
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.reflection import ReflectionEntry
from aureon.domain.models.student_profile import ConfidenceSnapshot, StudentProfile

NOW = datetime(2026, 1, 30, tzinfo=timezone.utc)


def test_empty_profile_is_insufficient_evidence():
    profile = StudentProfile(student_id="s1")
    bundle = assemble_progress_evidence(profile, now=NOW)

    assert bundle.insufficient_evidence is True
    assert bundle.total_evidence_count < MIN_EVIDENCE_FOR_PROGRESS_REPORT
    assert bundle.insufficient_evidence_reason is not None
    assert all(dim.direction == "not_enough_evidence" for dim in bundle.dimensions if dim.key != "career_clarity")


def test_more_recent_activity_than_previous_is_improving():
    profile = StudentProfile(student_id="s1")
    # 3 exploration events in the last week, only 1 in the previous 23 days.
    profile.career_exploration_history = [
        CareerExplorationEvent(id="1", career_id="c1", interaction_type="opened", created_at=NOW - timedelta(days=1)),
        CareerExplorationEvent(id="2", career_id="c2", interaction_type="opened", created_at=NOW - timedelta(days=2)),
        CareerExplorationEvent(id="3", career_id="c3", interaction_type="opened", created_at=NOW - timedelta(days=3)),
        CareerExplorationEvent(id="4", career_id="c4", interaction_type="opened", created_at=NOW - timedelta(days=20)),
    ]

    bundle = assemble_progress_evidence(profile, now=NOW)
    exploration = next(d for d in bundle.dimensions if d.key == "exploration")

    assert exploration.direction == "improving"
    assert "3 career exploration events in the last 7 days" in exploration.evidence_summary[0]


def test_reflection_stopped_recently_is_slowing():
    profile = StudentProfile(student_id="s1")
    # The spec's own worked example: reflection activity in the past month, none this week.
    profile.reflection_journal = [
        ReflectionEntry(prompt="p1", response="r1", answered_at=NOW - timedelta(days=10)),
        ReflectionEntry(prompt="p2", response="r2", answered_at=NOW - timedelta(days=15)),
    ]

    bundle = assemble_progress_evidence(profile, now=NOW)
    reflection = next(d for d in bundle.dimensions if d.key == "reflection_consistency")

    assert reflection.direction == "slowing"


def test_career_clarity_reflects_confidence_score_trend():
    profile = StudentProfile(student_id="s1")
    profile.confidence_score = 0.7
    profile.confidence_history = [
        ConfidenceSnapshot(score=0.2, source_agent="discovery", recorded_at=NOW - timedelta(days=25)),
        ConfidenceSnapshot(score=0.7, source_agent="discovery", recorded_at=NOW - timedelta(days=1)),
    ]

    bundle = assemble_progress_evidence(profile, now=NOW)
    clarity = next(d for d in bundle.dimensions if d.key == "career_clarity")

    assert clarity.direction == "improving"
    assert "0.20" in clarity.evidence_summary[0] and "0.70" in clarity.evidence_summary[0]


def test_skill_development_uses_observation_notebook_entries_only():
    profile = StudentProfile(student_id="s1")
    profile.notebook_entries = [
        NotebookEntry(id="1", kind="observation", text="x", source="conversation", created_at=NOW - timedelta(days=1)),
        NotebookEntry(id="2", kind="belief_revision", text="x", source="conversation", created_at=NOW - timedelta(days=1)),
    ]

    bundle = assemble_progress_evidence(profile, now=NOW)
    skill = next(d for d in bundle.dimensions if d.key == "skill_development")

    # Only the "observation" entry counts, not the "belief_revision" one.
    assert "1 new Career DNA observations in the last 7 days" in skill.evidence_summary[0]


def test_timeline_windows_are_pure_counts_no_fabrication():
    profile = StudentProfile(student_id="s1")
    profile.notebook_entries = [
        NotebookEntry(id="1", kind="observation", text="x", source="conversation", created_at=NOW - timedelta(days=2)),
    ]

    bundle = assemble_progress_evidence(profile, now=NOW)
    last_week = next(w for w in bundle.timeline if w.label == "Last Week")

    assert last_week.event_count == 1
