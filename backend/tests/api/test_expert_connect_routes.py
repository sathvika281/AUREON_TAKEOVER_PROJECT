import pytest

from aureon.api import deps
from aureon.domain.models.mentor import Mentor
from aureon.main import app
from tests.domain._explore_factories import make_career


class _FakeExpertRepository:
    def __init__(self, experts: list[Mentor]) -> None:
        self._experts = experts

    async def search_experts(
        self, *, q=None, specialization=None, industry=None, country=None,
        min_years_experience=None, accepts_mentorship=None, limit=100, offset=0,
    ):
        results = self._experts
        if specialization:
            results = [e for e in results if e.specialization == specialization]
        if industry:
            results = [e for e in results if industry in e.industries]
        if country:
            results = [e for e in results if e.country == country]
        if min_years_experience is not None:
            results = [e for e in results if e.years_experience >= min_years_experience]
        if accepts_mentorship is not None:
            results = [e for e in results if e.accepts_mentorship == accepts_mentorship]
        total = len(results)
        return results[offset : offset + limit], total

    async def get_expert(self, expert_id: str) -> Mentor | None:
        return next((e for e in self._experts if e.id == expert_id), None)

    async def list_filter_values(self):
        specializations = sorted({e.specialization for e in self._experts if e.specialization})
        industries = sorted({i for e in self._experts for i in e.industries})
        countries = sorted({e.country for e in self._experts if e.country})
        return specializations, industries, countries


class _FakeCareerRepository:
    def __init__(self, careers) -> None:
        self._careers = careers

    async def list_careers(self, **_kwargs):
        return self._careers

    async def get_career(self, career_id: str):
        return next((c for c in self._careers if c.id == career_id), None)


class _FakeCareerEventRepository:
    async def list_career_events(self, **_kwargs):
        return []


class _FakeMentorshipRepository:
    async def list_for_expert(self, expert_id: str):
        return []


def _expert(**overrides) -> Mentor:
    defaults: dict = dict(
        id="expert_1", name="Test Expert", role_type="industry_professional", field="technology",
        bio="A test expert.", learning_style_fit="x", profession="Software Engineer",
        specialization="Backend systems", country="Testland", years_experience=5,
        industries=["technology"], career_ids=["c1"],
        who_should_talk_to_me=["Students who like mathematics"],
    )
    defaults.update(overrides)
    return Mentor(**defaults)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    experts = [_expert(id="expert_1"), _expert(id="expert_2", country="Otherland", specialization="Frontend")]
    careers = [make_career(id="c1", name="Software Engineer", books=["Book A"])]

    app.dependency_overrides[deps.get_expert_repository] = lambda: _FakeExpertRepository(experts)
    app.dependency_overrides[deps.get_career_repository] = lambda: _FakeCareerRepository(careers)
    app.dependency_overrides[deps.get_career_event_repository] = lambda: _FakeCareerEventRepository()
    app.dependency_overrides[deps.get_mentorship_repository] = lambda: _FakeMentorshipRepository()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_expert_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)
        app.dependency_overrides.pop(deps.get_career_event_repository, None)
        app.dependency_overrides.pop(deps.get_mentorship_repository, None)


def test_search_experts_returns_paginated_results(api_client):
    response = api_client.get("/v1/experts")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["experts"]) == 2


def test_search_experts_filters_by_country(api_client):
    response = api_client.get("/v1/experts", params={"country": "Otherland"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["experts"][0]["id"] == "expert_2"


def test_search_experts_respects_limit_and_offset(api_client):
    response = api_client.get("/v1/experts", params={"limit": 1, "offset": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["experts"]) == 1
    assert body["limit"] == 1
    assert body["offset"] == 1


def test_get_expert_filters_returns_distinct_values(api_client):
    response = api_client.get("/v1/experts/filters")
    assert response.status_code == 200
    body = response.json()
    assert "Backend systems" in body["specializations"]
    assert "Frontend" in body["specializations"]
    assert "Testland" in body["countries"]


def test_get_expert_detail_resolves_linked_careers_and_suggested_knowledge(api_client):
    response = api_client.get("/v1/experts/expert_1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "expert_1"
    assert body["linked_careers"][0]["name"] == "Software Engineer"
    assert "who_should_talk_to_me" in body
    assert body["who_should_talk_to_me"] == ["Students who like mathematics"]


def test_get_expert_detail_404_for_unknown_expert(api_client):
    response = api_client.get("/v1/experts/does_not_exist")
    assert response.status_code == 404
