from datetime import datetime, timezone

from aureon.domain.models.project import Project, ProjectAttemptEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.project_result import complete_project_attempt

NOW = datetime.now(timezone.utc)


def _project(**overrides) -> Project:
    defaults: dict = dict(
        id="genomics_dataset_explorer", title="Genomics Dataset Explorer",
        brief="Explore a real genomics dataset.", difficulty_level="intermediate", estimated_hours=8,
        target_skill_ids=["programming", "statistical_analysis"],
    )
    defaults.update(overrides)
    return Project(**defaults)


def _profile() -> StudentProfile:
    return StudentProfile(student_id="s1")


def test_completion_with_artifact_url_writes_evidence_for_each_target_skill():
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence(artifact_url="https://github.com/example/repo")

    attempt = complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    assert len(profile.project_attempts) == 1
    assert profile.project_attempts[0].id == attempt.id
    skill_evidence = [e for e in profile.evidence_graph if e.source == "project"]
    assert len(skill_evidence) == 2
    assert {e.related_skill for e in skill_evidence} == {"programming", "statistical_analysis"}
    assert all(e.relation == "supports" for e in skill_evidence)


def test_completion_with_reflection_only_writes_evidence():
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence(reflection="I learned how to parse a real VCF file.")

    complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    skill_evidence = [e for e in profile.evidence_graph if e.source == "project"]
    assert len(skill_evidence) == 2
    assert all("VCF file" in e.text for e in skill_evidence)


def test_completion_with_neither_artifact_nor_reflection_writes_no_evidence():
    # The genuine-engagement gate: completion alone is never evidence.
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence()

    attempt = complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    # The attempt itself is still recorded — honest that it happened —
    # but it must not inflate the Evidence Graph.
    assert len(profile.project_attempts) == 1
    assert attempt.evidence.artifact_url is None
    assert profile.evidence_graph == []


def test_completion_with_whitespace_only_reflection_writes_no_evidence():
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence(reflection="   ")

    complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    assert profile.evidence_graph == []


def test_completion_does_not_reinforce_any_world_signal():
    # Project has no related_world — unlike Experiment, completion must
    # never touch discovery_onboarding.world_signals.
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence(artifact_url="https://github.com/example/repo")

    complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    assert profile.discovery_onboarding.world_signals == []


def test_repeat_completion_does_not_duplicate_identical_evidence():
    # Same dedup discipline as record_new_evidence's other callers.
    profile = _profile()
    project = _project()
    evidence = ProjectAttemptEvidence(reflection="Same reflection text.")

    complete_project_attempt(profile, project, evidence=evidence, now=NOW)
    complete_project_attempt(profile, project, evidence=evidence, now=NOW)

    assert len(profile.project_attempts) == 2
    skill_evidence = [e for e in profile.evidence_graph if e.source == "project"]
    assert len(skill_evidence) == 2  # still one per target skill, not four
