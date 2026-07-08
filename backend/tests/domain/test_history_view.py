from datetime import datetime, timedelta, timezone

from aureon.domain.models.career_comparison import CareerComparison, ParallelUniverseBranch, ParallelUniverseScenario
from aureon.domain.models.career_investigation import CareerInvestigationRecord
from aureon.domain.models.career_simulation import CareerSimulation
from aureon.domain.models.document_investigation import DocumentInvestigationRecord
from aureon.domain.models.github_investigation import GitHubInvestigationRecord
from aureon.domain.models.mentor_match import CollegeMatch, MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.history_view import build_history_items
from aureon.shared.types import AgentName

NOW = datetime.now(timezone.utc)


def test_empty_profile_returns_no_history():
    profile = StudentProfile(student_id="s1")
    assert build_history_items(profile) == []


def test_aggregates_all_record_types_with_correct_type_and_specialist():
    profile = StudentProfile(student_id="s1")

    profile.career_comparisons.append(CareerComparison(
        id="c1", career_ids=["a", "b"], career_names={"a": "AI Research", "b": "Robotics"},
        dimensions=[], summary_reason="x", created_at=NOW,
    ))
    profile.parallel_universe_scenarios.append(ParallelUniverseScenario(
        id="p1", branches=[
            ParallelUniverseBranch(career_id="a", career_name="AI Research", daily_work="x", lifestyle="x", growth="x", challenges="x", future_opportunities="x"),
        ], created_at=NOW,
    ))
    profile.career_investigations.append(CareerInvestigationRecord(
        id="i1", question="Should I pursue AI Research?", overall_summary="x", created_at=NOW,
    ))
    profile.career_simulations.append(CareerSimulation(
        id="sim1", career_ids=["a"], career_names={"a": "AI Research"}, created_at=NOW,
    ))
    profile.github_investigations.append(GitHubInvestigationRecord(
        id="g1", url="https://github.com/someone/repo", owner="someone", repo="repo",
        name="repo", description="x", overall_summary="x", project_purpose="x", technical_complexity="x",
        problem_solving="x", code_organization="x", technology_breadth="x", documentation_quality="x",
        learning_signals="x", engineering_maturity="x", research_orientation="x", ai_ml_signals="x", created_at=NOW,
    ))
    profile.document_investigations.append(DocumentInvestigationRecord(
        id="d1", filename="resume.pdf", category="resume", owning_specialist=AgentName.DISCOVERY.value, created_at=NOW,
    ))
    profile.mentor_matches.append(MentorMatch(
        id="m1", mentor_id="mentor-1", mentor_name="Dr. Real Mentor", why_it_matches="x", confidence=0.7, created_at=NOW, updated_at=NOW,
    ))
    profile.college_matches.append(CollegeMatch(
        id="col1", institution_id="inst-1", institution_name="Real University", why_it_matches="x", confidence=0.7, created_at=NOW, updated_at=NOW,
    ))

    items = build_history_items(profile)

    assert len(items) == 8
    by_type = {i.mission_type: i for i in items}
    assert by_type["career_comparison"].mission_name == "Compared AI Research vs Robotics"
    assert by_type["career_comparison"].owning_specialist == AgentName.DECISION.value
    assert by_type["parallel_universe"].owning_specialist == AgentName.DECISION.value
    assert by_type["search_investigation"].mission_name == "Should I pursue AI Research?"
    assert by_type["search_investigation"].owning_specialist == AgentName.CAREER_INTELLIGENCE.value
    assert by_type["career_simulation"].owning_specialist == AgentName.DECISION.value
    assert by_type["github_investigation"].mission_name == "Investigated someone/repo"
    assert by_type["github_investigation"].owning_specialist == AgentName.DISCOVERY.value
    assert by_type["document_investigation"].mission_name == "Analyzed resume.pdf"
    assert by_type["document_investigation"].owning_specialist == AgentName.DISCOVERY.value
    assert by_type["mentor_match"].mission_name == "Matched with Dr. Real Mentor"
    assert by_type["institution_match"].mission_name == "Matched with Real University"
    assert all(i.status == "completed" for i in items)
    # Every type's artifact_id is a real, frontend-retrievable id — mentor/
    # institution matches use their catalog id (mentor_id/institution_id)
    # since the MentorMatchDTO/CollegeMatchDTO never exposes the match
    # record's own internal id.
    assert by_type["mentor_match"].artifact_id == "mentor-1"
    assert by_type["institution_match"].artifact_id == "inst-1"
    non_match_types = {k: v for k, v in by_type.items() if k not in ("mentor_match", "institution_match")}
    assert all(i.artifact_id == i.id for i in non_match_types.values())


def test_items_are_sorted_newest_first():
    profile = StudentProfile(student_id="s1")
    older = NOW - timedelta(days=1)
    profile.career_investigations.append(CareerInvestigationRecord(
        id="old", question="old question", overall_summary="x", created_at=older,
    ))
    profile.career_investigations.append(CareerInvestigationRecord(
        id="new", question="new question", overall_summary="x", created_at=NOW,
    ))

    items = build_history_items(profile)

    assert [i.id for i in items] == ["new", "old"]
