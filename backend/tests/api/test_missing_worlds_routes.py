import pytest

from aureon.api import deps
from aureon.domain.models.career_world import CareerWorld
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


def _world(**overrides) -> CareerWorld:
    defaults = dict(
        id="world_space", name="Space", description="d", why_it_matters="w", global_importance="g",
        future_growth="f", related_industries=["space"],
    )
    defaults.update(overrides)
    return CareerWorld(**defaults)


class _FakeCareerWorldRepository:
    def __init__(self, worlds):
        self._worlds = worlds

    async def list_worlds(self):
        return self._worlds


class _FakeCareerRepository:
    async def list_careers(self, **_kwargs):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_career_world_repository] = lambda: _FakeCareerWorldRepository([_world()])
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository()
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_career_world_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)


def test_get_missing_worlds_returns_every_world_classified(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/missing-worlds")

    assert response.status_code == 200
    body = response.json()
    assert len(body["worlds"]) == 1
    assert body["worlds"][0]["exploration_level"] == "unexplored"
    assert body["worlds"][0]["world"]["name"] == "Space"


def test_get_missing_worlds_reflects_real_interests(api_client):
    client, fake_profiles = api_client
    fake_profiles._profiles[STUDENT_ID].interests.append("space exploration")

    response = client.get(f"/v1/students/{STUDENT_ID}/missing-worlds")

    body = response.json()
    assert body["worlds"][0]["exploration_level"] == "partially_explored"
    assert "world_space" in body["recommended_next"]
