import pytest

from aureon.api import deps
from aureon.domain.models.discovery_onboarding import WorldSignal
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.domain._explore_factories import make_career
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


class _FakeCareerRepository:
    def __init__(self, careers):
        self._careers = list(careers)

    async def list_careers(self, *, category=None, industry=None, country=None, q=None):
        return list(self._careers)

    async def get_career(self, career_id):
        return next((c for c in self._careers if c.id == career_id), None)

    async def list_stories_for_career(self, career_id):
        return []


class _FakeTrendRepository:
    async def list_trends(self, *, category=None, industry=None, region=None):
        return []


class _FakeProjectRepository:
    async def list_projects_for_career(self, career_id):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    profile = StudentProfile(student_id=STUDENT_ID)
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: profile})
    fake_careers = _FakeCareerRepository(
        [
            make_career(id="ai_1", industry="technology", category="emerging", name="AI Engineer", trait_tags=["curiosity"]),
            make_career(id="ai_2", industry="technology", category="emerging", name="ML Researcher", trait_tags=["curiosity"]),
            make_career(id="bio_1", industry="healthcare", category="traditional", name="Nurse", trait_tags=["leadership"]),
        ]
    )
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_trend_repository] = lambda: _FakeTrendRepository()
    app.dependency_overrides[deps.get_project_repository] = lambda: _FakeProjectRepository()
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_career_repository, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_trend_repository, None)
        app.dependency_overrides.pop(deps.get_project_repository, None)


def test_list_careers_without_student_id_returns_full_catalog_unordered_change(api_client):
    client, _ = api_client
    response = client.get("/v1/careers")
    assert response.status_code == 200
    assert len(response.json()) == 3  # nothing filtered out


def test_list_careers_with_student_id_reorders_never_filters(api_client):
    client, _ = api_client
    from datetime import datetime, timezone

    profile = StudentProfile(student_id=STUDENT_ID)
    profile.discovery_onboarding.world_signals = [
        WorldSignal(world="Healthcare", confidence=0.9, evidence=[], status="curious",
                    first_observed=datetime.now(timezone.utc), last_reinforced=datetime.now(timezone.utc))
    ]
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: FakeStudentProfileRepository(
        {STUDENT_ID: profile}
    )

    response = client.get("/v1/careers", params={"student_id": STUDENT_ID})

    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert set(ids) == {"ai_1", "ai_2", "bio_1"}  # still every career — reorder, never filter
    assert ids[0] == "bio_1"  # the aligned one now leads


def test_career_detail_includes_related_careers_and_new_fields(api_client):
    client, _ = api_client
    response = client.get("/v1/careers/ai_1")
    assert response.status_code == 200
    body = response.json()
    assert body["related_careers"][0]["id"] == "ai_2"  # real industry+trait match
    assert "description" in body
    assert "why_people_love_it" in body
    assert "branches" in body


def test_career_detail_recommends_unvisited_related_career(api_client):
    client, _ = api_client
    response = client.get("/v1/careers/ai_1", params={"student_id": STUDENT_ID})
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_next_exploration"]["id"] == "ai_2"


def test_career_detail_404_for_unknown_career(api_client):
    client, _ = api_client
    response = client.get("/v1/careers/does_not_exist")
    assert response.status_code == 404
