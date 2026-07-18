from datetime import datetime, timezone

from aureon.domain.models.mentor_handoff import MentorHandoff
from aureon.domain.models.mentor_match import MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.services.foundation.career_memory.service import (
    get_career_memory_snapshot,
    get_connections,
    get_identity,
    record_evidence_artifact,
    record_growth_mission,
    record_growth_skill,
    record_interview_practice,
    record_opportunity_entry,
)

NOW = datetime.now(timezone.utc)


def test_record_and_snapshot_round_trip_every_new_domain():
    profile = StudentProfile(student_id="s1")

    record_evidence_artifact(profile, kind="project", ref_id="proj_1", title="Robotics Arm", now=NOW)
    record_opportunity_entry(
        profile, interaction="viewed", category="internship", ref_id=None,
        opportunity_version=None, title="Summer AI Internship", now=NOW,
    )
    record_growth_skill(profile, skill="Python", status="mastered", evidence="Shipped 3 projects")
    record_growth_mission(profile, mission_id="mission_1", status="completed")
    record_interview_practice(profile, weak_areas=["system design"], feedback_summary="Practice whiteboarding", now=NOW)

    snapshot = get_career_memory_snapshot(profile)

    assert snapshot.evidence.artifacts[0].ref_id == "proj_1"
    assert snapshot.opportunities.entries[0].title == "Summer AI Internship"
    assert snapshot.growth.skills[0].skill == "Python"
    assert snapshot.growth.missions[0].status == "completed"
    assert snapshot.growth.interview_practice[0].weak_areas == ["system design"]


def test_get_identity_facades_new_field_only():
    profile = StudentProfile(student_id="s1")
    identity = get_identity(profile)
    assert identity.preferred_industries == []


def test_get_connections_derives_from_mentor_matches_without_explicit_record_call():
    profile = StudentProfile(student_id="s1")
    profile.mentor_matches.append(
        MentorMatch(
            id="m1", mentor_id="mentor_1", mentor_name="Dr. Ada", why_it_matches="shared curiosity",
            confidence=0.6, status="active", updated_at=NOW,
        )
    )
    profile.mentor_interactions.append(
        MentorHandoff(reason="Discussed research paths", requested_by_agent="mentor", resolved=True, mentor_id="mentor_1")
    )

    connections = get_connections(profile)

    assert len(connections.connections) == 1
    assert connections.connections[0].mentor_name == "Dr. Ada"
    assert connections.connections[0].conversation_summary == "Discussed research paths"


def test_get_connections_excludes_discarded_matches():
    profile = StudentProfile(student_id="s1")
    profile.mentor_matches.append(
        MentorMatch(
            id="m1", mentor_id="mentor_1", mentor_name="Dr. Ada", why_it_matches="x",
            confidence=0.6, status="discarded", updated_at=NOW,
        )
    )

    assert get_connections(profile).connections == []
