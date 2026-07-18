import pytest

from aureon.api import deps
from aureon.domain.models.trend import Trend
from aureon.main import app


class _FakeTrendRepository:
    def __init__(self, trends):
        self._trends = trends

    async def list_trends(self, *, category=None, industry=None, region=None):
        results = self._trends
        if category:
            results = [t for t in results if t.category == category]
        if industry:
            results = [t for t in results if industry.lower() in {i.lower() for i in t.affected_industries}]
        return results


def _trend(**overrides) -> Trend:
    defaults: dict = dict(
        id="trend_1", title="Test Trend", category="skill_shift", summary="x", description="x",
        time_horizon="near_term", affected_skills=["python"], affected_industries=["technology"],
    )
    defaults.update(overrides)
    return Trend(**defaults)


@pytest.fixture
def client_with_trends():
    from fastapi.testclient import TestClient

    fake_repo = _FakeTrendRepository([_trend(id="t1"), _trend(id="t2", category="ai_influence", affected_skills=["ml"])])
    app.dependency_overrides[deps.get_trend_repository] = lambda: fake_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_trend_repository, None)


def test_list_trends_returns_all_by_default(client_with_trends):
    response = client_with_trends.get("/v1/trends")
    assert response.status_code == 200
    assert len(response.json()["trends"]) == 2


def test_list_trends_filters_by_category(client_with_trends):
    response = client_with_trends.get("/v1/trends", params={"category": "ai_influence"})
    assert response.status_code == 200
    trends = response.json()["trends"]
    assert len(trends) == 1
    assert trends[0]["id"] == "t2"


def test_future_skills_aggregates_real_seeded_skills(client_with_trends):
    response = client_with_trends.get("/v1/trends/future-skills")
    assert response.status_code == 200
    skills = {s["skill"] for s in response.json()["skills"]}
    assert skills == {"python", "ml"}
