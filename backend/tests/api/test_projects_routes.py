from datetime import datetime, timedelta, timezone

import pytest

from aureon.api import deps
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.company import Company
from aureon.domain.models.project import Project, ProjectAttempt, ProjectAttemptEvidence
from aureon.domain.models.skill import Skill
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"

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


class _FakeProjectRepository:
    def __init__(self, projects):
        self._projects = list(projects)

    async def list_projects(self, *, difficulty_level=None):
        results = self._projects
        if difficulty_level:
            results = [p for p in results if p.difficulty_level == difficulty_level]
        return results

    async def get_project(self, project_id):
        return next((p for p in self._projects if p.id == project_id), None)

    async def list_projects_for_career(self, career_id):
        return [p for p in self._projects if career_id in p.related_career_ids]


class _FakeSkillRepository:
    def __init__(self, skills):
        self._skills = list(skills)

    async def list_by_ids(self, skill_ids):
        return [s for s in self._skills if s.id in skill_ids]


class _FakeCareerRepository:
    def __init__(self, careers):
        self._careers = list(careers)

    async def list_by_ids(self, career_ids):
        return [c for c in self._careers if c.id in career_ids]


class _FakeCompanyRepository:
    def __init__(self, companies):
        self._companies = list(companies)

    async def list_by_ids(self, company_ids):
        return [c for c in self._companies if c.id in company_ids]


def _project(**overrides) -> Project:
    defaults: dict = dict(
        id="genomics_dataset_explorer", title="Genomics Dataset Explorer",
        brief="Explore a real genomics dataset.", difficulty_level="intermediate", estimated_hours=8,
        target_skill_ids=["programming"], related_career_ids=["genomics_data_scientist"],
    )
    defaults.update(overrides)
    return Project(**defaults)


def _skill(**overrides) -> Skill:
    defaults: dict = dict(id="programming", name="Programming", category="technical", description="x")
    defaults.update(overrides)
    return Skill(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
    )
    defaults.update(overrides)
    return Career(**defaults)


def _company(**overrides) -> Company:
    defaults: dict = dict(id="illumina", name="Illumina", organization_kind="company", industry="biotechnology", what_they_do="x")
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def client_with_projects():
    from fastapi.testclient import TestClient

    fake_projects = _FakeProjectRepository(
        [_project(id="genomics_dataset_explorer"), _project(id="bridge_load_simulation", difficulty_level="advanced")]
    )
    fake_skills = _FakeSkillRepository([_skill()])
    fake_careers = _FakeCareerRepository([_career()])
    fake_companies = _FakeCompanyRepository([_company()])
    app.dependency_overrides[deps.get_project_repository] = lambda: fake_projects
    app.dependency_overrides[deps.get_skill_repository] = lambda: fake_skills
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    app.dependency_overrides[deps.get_company_repository] = lambda: fake_companies
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_project_repository, None)
        app.dependency_overrides.pop(deps.get_skill_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)
        app.dependency_overrides.pop(deps.get_company_repository, None)


def test_list_projects_returns_all_by_default(client_with_projects):
    response = client_with_projects.get("/v1/projects")
    assert response.status_code == 200
    assert len(response.json()["projects"]) == 2


def test_list_projects_filters_by_difficulty(client_with_projects):
    response = client_with_projects.get("/v1/projects", params={"difficulty_level": "advanced"})
    assert response.status_code == 200
    projects = response.json()["projects"]
    assert len(projects) == 1
    assert projects[0]["id"] == "bridge_load_simulation"


def test_get_project_returns_real_resolved_entities(client_with_projects):
    response = client_with_projects.get("/v1/projects/genomics_dataset_explorer")
    assert response.status_code == 200
    body = response.json()
    assert body["project"]["id"] == "genomics_dataset_explorer"
    assert len(body["target_skills"]) == 1
    assert body["target_skills"][0]["id"] == "programming"
    assert len(body["related_careers"]) == 1
    assert body["related_careers"][0]["id"] == "genomics_data_scientist"


def test_get_unknown_project_returns_404(client_with_projects):
    response = client_with_projects.get("/v1/projects/does-not-exist")
    assert response.status_code == 404


def test_get_project_without_student_id_returns_no_attempts(client_with_projects):
    """Backward-compatible default — omitting student_id behaves exactly
    as it did before Sprint 7."""
    response = client_with_projects.get("/v1/projects/genomics_dataset_explorer")
    assert response.status_code == 200
    assert response.json()["attempts"] == []


@pytest.fixture
def client_with_projects_and_profiles():
    from fastapi.testclient import TestClient

    fake_projects = _FakeProjectRepository(
        [_project(id="genomics_dataset_explorer"), _project(id="bridge_load_simulation", difficulty_level="advanced")]
    )
    fake_skills = _FakeSkillRepository([_skill()])
    fake_careers = _FakeCareerRepository([_career()])
    fake_companies = _FakeCompanyRepository([_company()])
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_project_repository] = lambda: fake_projects
    app.dependency_overrides[deps.get_skill_repository] = lambda: fake_skills
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    app.dependency_overrides[deps.get_company_repository] = lambda: fake_companies
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_project_repository, None)
        app.dependency_overrides.pop(deps.get_skill_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)
        app.dependency_overrides.pop(deps.get_company_repository, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)


def _attempt(**overrides) -> ProjectAttempt:
    defaults: dict = dict(
        id="attempt-1", project_id="genomics_dataset_explorer", project_title="Genomics Dataset Explorer",
        target_skill_ids=["programming"], attempted_at=datetime.now(timezone.utc),
        evidence=ProjectAttemptEvidence(),
    )
    defaults.update(overrides)
    return ProjectAttempt(**defaults)


def test_get_project_with_student_id_and_no_attempts_returns_empty_list(client_with_projects_and_profiles):
    client, _ = client_with_projects_and_profiles
    response = client.get("/v1/projects/genomics_dataset_explorer", params={"student_id": STUDENT_ID})
    assert response.status_code == 200
    assert response.json()["attempts"] == []


def test_get_project_with_student_id_returns_own_attempts_most_recent_first(client_with_projects_and_profiles):
    client, fake_profiles = client_with_projects_and_profiles
    now = datetime.now(timezone.utc)
    older = _attempt(id="older", attempted_at=now - timedelta(days=2))
    newer = _attempt(
        id="newer", attempted_at=now,
        evidence=ProjectAttemptEvidence(artifact_url="https://github.com/example/repo", reflection="Real work."),
    )
    profile = fake_profiles._profiles[STUDENT_ID]
    profile.project_attempts.extend([older, newer])

    response = client.get("/v1/projects/genomics_dataset_explorer", params={"student_id": STUDENT_ID})
    assert response.status_code == 200
    attempts = response.json()["attempts"]
    assert [a["id"] for a in attempts] == ["newer", "older"]
    assert attempts[0]["evidence"]["artifact_url"] == "https://github.com/example/repo"
    assert attempts[1]["evidence"]["artifact_url"] is None


def test_get_project_with_student_id_excludes_other_projects_attempts(client_with_projects_and_profiles):
    client, fake_profiles = client_with_projects_and_profiles
    profile = fake_profiles._profiles[STUDENT_ID]
    profile.project_attempts.append(_attempt(id="other", project_id="bridge_load_simulation"))

    response = client.get("/v1/projects/genomics_dataset_explorer", params={"student_id": STUDENT_ID})
    assert response.status_code == 200
    assert response.json()["attempts"] == []


@pytest.fixture
def completion_client():
    from fastapi.testclient import TestClient

    fake_projects = _FakeProjectRepository([_project()])
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_project_repository] = lambda: fake_projects
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_project_repository, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)


def test_complete_project_attempt_records_and_writes_evidence(completion_client):
    client, fake_profiles = completion_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/projects/genomics_dataset_explorer/complete",
        json={"artifact_url": "https://github.com/example/repo", "reflection": "Built a real dataset explorer."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "genomics_dataset_explorer"
    assert body["evidence"]["artifact_url"] == "https://github.com/example/repo"

    saved = fake_profiles.saved[-1]
    assert len(saved.project_attempts) == 1
    skill_evidence = [e for e in saved.evidence_graph if e.source == "project"]
    # Both artifact_url and reflection were real -> two evidence strings,
    # both attributed to the project's one target skill.
    assert len(skill_evidence) == 2
    assert all(e.related_skill == "programming" for e in skill_evidence)


def test_complete_project_attempt_with_no_real_content_writes_no_evidence(completion_client):
    client, fake_profiles = completion_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/projects/genomics_dataset_explorer/complete",
        json={},
    )

    assert response.status_code == 200
    saved = fake_profiles.saved[-1]
    assert len(saved.project_attempts) == 1
    assert saved.evidence_graph == []


def test_complete_unknown_project_returns_404(completion_client):
    client, _ = completion_client
    response = client.post(f"/v1/students/{STUDENT_ID}/projects/does-not-exist/complete", json={})
    assert response.status_code == 404
