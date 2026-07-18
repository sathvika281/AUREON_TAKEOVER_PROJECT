import pytest

from aureon.api import deps
from aureon.domain.models.knowledge_circle import KnowledgeCircle
from aureon.main import app
from tests.domain._connect_factories import make_knowledge_circle
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "student_1"


class _FakeKnowledgeCircleRepository:
    def __init__(self, circles: list[KnowledgeCircle]) -> None:
        self._circles = circles

    async def list_circles(self, *, q=None):
        results = self._circles
        if q:
            results = [c for c in results if q.lower() in c.name.lower()]
        return results

    async def get_circle(self, circle_id: str):
        return next((c for c in self._circles if c.id == circle_id), None)


class _FakeCareerWorldRepository:
    async def get_world(self, world_id: str):
        return None


class _FakeTopicResourceRepository:
    async def list_domains(self):
        return []


class _FakeCareerRepository:
    async def list_careers(self, **_kwargs):
        return []


class _FakeTrendRepository:
    async def list_trends(self, **_kwargs):
        return []


class _FakeLifeMissionRepository:
    async def list_missions(self):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    circles = [make_knowledge_circle(id="circle_1", name="Space", overview="Real overview.")]
    profiles = FakeStudentProfileRepository()

    app.dependency_overrides[deps.get_knowledge_circle_repository] = lambda: _FakeKnowledgeCircleRepository(circles)
    app.dependency_overrides[deps.get_career_world_repository] = lambda: _FakeCareerWorldRepository()
    app.dependency_overrides[deps.get_topic_resource_repository] = lambda: _FakeTopicResourceRepository()
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository()
    app.dependency_overrides[deps.get_trend_repository] = lambda: _FakeTrendRepository()
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: _FakeLifeMissionRepository()
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: profiles
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    try:
        yield TestClient(app)
    finally:
        for dep in (
            deps.get_knowledge_circle_repository, deps.get_career_world_repository,
            deps.get_topic_resource_repository, deps.get_career_repository,
            deps.get_trend_repository, deps.get_life_mission_repository,
            deps.get_student_profile_repository, deps.get_current_user_id,
        ):
            app.dependency_overrides.pop(dep, None)


def test_list_knowledge_circles_is_open_no_auth_required(api_client):
    response = api_client.get("/v1/knowledge-circles")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["name"] == "Space"


def test_get_knowledge_circle_composes_a_full_view(api_client):
    response = api_client.get("/v1/knowledge-circles/circle_1")
    assert response.status_code == 200
    body = response.json()
    assert body["overview"] == "Real overview."
    assert body["books"] == []


def test_get_knowledge_circle_404_for_unknown_circle(api_client):
    response = api_client.get("/v1/knowledge-circles/does_not_exist")
    assert response.status_code == 404


def test_bookmark_resource_requires_the_authenticated_student(api_client):
    response = api_client.post(
        f"/v1/students/{STUDENT_ID}/knowledge-circles/circle_1/bookmark",
        json={"resource_type": "books", "resource_label": "A Real Book"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["progress"][0]["status"] == "bookmarked"
    assert body["progress"][0]["resource_label"] == "A Real Book"


def test_bookmark_resource_rejects_a_different_students_path(api_client):
    response = api_client.post(
        "/v1/students/someone-else/knowledge-circles/circle_1/bookmark",
        json={"resource_type": "books", "resource_label": "A Real Book"},
    )
    assert response.status_code == 403


def test_complete_resource_then_progress_reflects_it(api_client):
    api_client.post(
        f"/v1/students/{STUDENT_ID}/knowledge-circles/circle_1/complete",
        json={"resource_type": "books", "resource_label": "A Real Book"},
    )
    response = api_client.get(f"/v1/students/{STUDENT_ID}/knowledge-circles/circle_1/progress")
    assert response.status_code == 200
    assert response.json()["progress"][0]["status"] == "completed"
