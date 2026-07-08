from datetime import datetime, timezone

from aureon.agents.specialized.decision.simulation_next_actions import build_next_actions
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.mentor_match import MentorMatch
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
CAREER = Career(id="ai_research", name="AI Research", category="research", industry="tech", one_liner="x", reality=_REALITY, future_lens=_FUTURE)


def test_no_mentor_match_yields_fallback_action_not_a_name():
    profile = StudentProfile(student_id="s1")
    actions = build_next_actions(CAREER, [], profile)
    assert any("Run Mentor Match" in a for a in actions)
    assert not any("Connect with" in a for a in actions)


def test_real_mentor_match_is_named_in_the_action():
    profile = StudentProfile(student_id="s1")
    now = datetime.now(timezone.utc)
    profile.mentor_matches.append(MentorMatch(
        id="m1", mentor_id="mentor-1", mentor_name="Dr. Real Mentor", why_it_matches="x", confidence=0.8,
        created_at=now, updated_at=now,
    ))

    actions = build_next_actions(CAREER, [], profile)

    assert any("Dr. Real Mentor" in a for a in actions)


def test_discarded_mentor_match_is_never_recommended():
    profile = StudentProfile(student_id="s1")
    now = datetime.now(timezone.utc)
    profile.mentor_matches.append(MentorMatch(
        id="m1", mentor_id="mentor-1", mentor_name="Discarded Mentor", why_it_matches="x", confidence=0.9,
        status="discarded", created_at=now, updated_at=now,
    ))

    actions = build_next_actions(CAREER, [], profile)

    assert not any("Discarded Mentor" in a for a in actions)


def test_compare_action_names_the_real_other_selected_careers():
    profile = StudentProfile(student_id="s1")
    actions = build_next_actions(CAREER, ["Robotics Engineering", "Startup Founder"], profile)
    compare_actions = [a for a in actions if a.startswith("Compare")]
    assert len(compare_actions) == 1
    assert "Robotics Engineering" in compare_actions[0]
    assert "Startup Founder" in compare_actions[0]


def test_no_compare_action_when_only_one_career_simulated():
    profile = StudentProfile(student_id="s1")
    actions = build_next_actions(CAREER, [], profile)
    assert not any(a.startswith("Compare") for a in actions)


def test_existing_search_investigation_suppresses_the_investigate_action():
    from aureon.domain.models.career_investigation import CareerInvestigationRecord

    profile = StudentProfile(student_id="s1")
    profile.career_investigations.append(CareerInvestigationRecord(
        id="i1", question="Should I pursue AI Research?", overall_summary="x", related_career_id="ai_research",
    ))

    actions = build_next_actions(CAREER, [], profile)

    assert not any("Search Intelligence" in a for a in actions)


def test_existing_github_evidence_suppresses_the_github_action():
    profile = StudentProfile(student_id="s1")
    profile.evidence_graph.append(EvidenceRecord(
        id="e1", text="x", source="github", relation="supports", created_at=datetime.now(timezone.utc),
    ))

    actions = build_next_actions(CAREER, [], profile)

    assert not any("GitHub Intelligence" in a for a in actions)
