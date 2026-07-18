from datetime import datetime, timezone

import pytest

from aureon.api import deps
from aureon.domain.models.exposure import ExposureHistoryEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.domain._connect_factories import make_career_story, make_expert, make_knowledge_circle
from tests.domain._explore_factories import make_career, make_career_world
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


class _FakeCareerRepository:
    def __init__(self, careers):
        self._careers = careers

    async def list_careers(self, **_kwargs):
        return self._careers


class _FakeExperimentRepository:
    def __init__(self, experiments=None):
        self._experiments = experiments or []

    async def list_experiments(self, **_kwargs):
        return self._experiments


class _FakeCareerWorldRepository:
    def __init__(self, worlds=None):
        self._worlds = worlds or []

    async def list_worlds(self, **_kwargs):
        return self._worlds


class _FakeKnowledgeCircleRepository:
    def __init__(self, circles=None):
        self._circles = circles or []

    async def list_circles(self, **_kwargs):
        return self._circles


class _FakeJourneyStoryRepository:
    def __init__(self, stories=None):
        self._stories = stories or []

    async def search_stories(self, *, career_id=None, limit=50, **_kwargs):
        matches = [s for s in self._stories if career_id is None or s.career_id == career_id]
        return matches[:limit], len(matches)


class _FakeExpertRepository:
    def __init__(self, experts=None):
        self._experts = experts or []

    async def search_experts(self, *, industry=None, limit=50, **_kwargs):
        matches = [e for e in self._experts if industry is None or industry in e.industries]
        return matches[:limit], len(matches)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    fake_careers = _FakeCareerRepository(
        [make_career(id="a", curiosity_hook="Real hook A"), make_career(id="b"), make_career(id="c")]
    )
    fake_experiments = _FakeExperimentRepository()
    fake_worlds = _FakeCareerWorldRepository(
        [make_career_world(id="world_1", name="World One", related_industries=["technology"])]
    )
    fake_circles = _FakeKnowledgeCircleRepository()
    fake_stories = _FakeJourneyStoryRepository()
    fake_experts = _FakeExpertRepository()

    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    app.dependency_overrides[deps.get_experiment_repository] = lambda: fake_experiments
    app.dependency_overrides[deps.get_career_world_repository] = lambda: fake_worlds
    app.dependency_overrides[deps.get_knowledge_circle_repository] = lambda: fake_circles
    app.dependency_overrides[deps.get_journey_story_repository] = lambda: fake_stories
    app.dependency_overrides[deps.get_expert_repository] = lambda: fake_experts
    try:
        yield TestClient(app), fake_profiles, fake_worlds, fake_circles, fake_stories, fake_experts
    finally:
        for dep in (
            deps.get_current_user_id, deps.get_student_profile_repository, deps.get_career_repository,
            deps.get_experiment_repository, deps.get_career_world_repository, deps.get_knowledge_circle_repository,
            deps.get_journey_story_repository, deps.get_expert_repository,
        ):
            app.dependency_overrides.pop(dep, None)


def test_get_exposure_universe_returns_real_suggestions(api_client):
    client, fake_profiles, *_ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe")

    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert 1 <= len(suggestions) <= 3
    for s in suggestions:
        assert s["curiosity_hook"]  # never empty

    saved = fake_profiles.saved[-1]
    assert len(saved.exposure_history) == len(suggestions)


def test_get_exposure_universe_includes_exposure_map_and_missing_worlds(api_client):
    client, *_ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe")

    body = response.json()
    assert "exposure_map" in body
    assert "engaged" in body["exposure_map"]
    assert "limited_or_none" in body["exposure_map"]
    assert body["missing_worlds"][0]["world"]["id"] == "world_1"
    assert body["missing_worlds"][0]["why_missing"]


def test_no_repeats_across_two_calls(api_client):
    client, *_ = api_client
    first = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe").json()["suggestions"]
    second = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe").json()["suggestions"]

    first_ids = {s["career"]["id"] for s in first}
    second_ids = {s["career"]["id"] for s in second}
    assert first_ids.isdisjoint(second_ids)


def test_record_interaction_updates_history(api_client):
    client, fake_profiles, *_ = api_client
    suggestions = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe").json()["suggestions"]
    career_id = suggestions[0]["career"]["id"]

    response = client.post(
        f"/v1/students/{STUDENT_ID}/exposure-universe/interact",
        json={"career_id": career_id, "interaction": "opened"},
    )

    assert response.status_code == 200
    assert response.json()["recorded"] is True
    saved = fake_profiles.saved[-1]
    entry = next(e for e in saved.exposure_history if e.career_id == career_id)
    assert entry.interaction == "opened"


def test_get_world_detail_returns_full_detail(api_client):
    client, fake_profiles, fake_worlds, fake_circles, fake_stories, fake_experts = api_client
    fake_worlds._worlds = [
        make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    ]
    fake_careers_repo = _FakeCareerRepository([make_career(id="c1", name="Marine Biologist", industry="marine biology")])
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers_repo
    fake_circles._circles = [make_knowledge_circle(id="circle_1", linked_career_world_id="world_marine")]
    fake_stories._stories = [make_career_story(id="story_1", career_id="c1")]
    fake_experts._experts = [make_expert(id="expert_1", industries=["marine biology"])]

    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe/worlds/world_marine")

    assert response.status_code == 200
    body = response.json()
    assert body["world"]["id"] == "world_marine"
    assert [c["id"] for c in body["related_careers"]] == ["c1"]
    assert [s["id"] for s in body["related_stories"]] == ["story_1"]
    assert [e["id"] for e in body["related_experts"]] == ["expert_1"]
    assert body["linked_circle"]["id"] == "circle_1"


def test_get_world_detail_404_for_unknown_world(api_client):
    client, *_ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe/worlds/does-not-exist")
    assert response.status_code == 404


def test_shown_interaction_does_not_change_world_level_but_opened_does(api_client):
    """End-to-end evolution check: a career merely shown does not move a
    world's exploration level; the same career actually opened does."""
    client, fake_profiles, fake_worlds, *_ = api_client
    fake_worlds._worlds = [
        make_career_world(id="world_marine", name="Marine Sciences", related_industries=["marine biology"])
    ]
    fake_careers_repo = _FakeCareerRepository([make_career(id="c1", name="Marine Biologist", industry="marine biology")])
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers_repo

    profile = fake_profiles._profiles[STUDENT_ID]
    profile.exposure_history.append(
        ExposureHistoryEntry(id="x1", career_id="c1", shown_at=datetime.now(timezone.utc), interaction="shown")
    )
    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe")
    world_card = response.json()["missing_worlds"][0]
    assert world_card["level"] == "unexplored"

    client.post(
        f"/v1/students/{STUDENT_ID}/exposure-universe/interact",
        json={"career_id": "c1", "interaction": "opened"},
    )
    response = client.get(f"/v1/students/{STUDENT_ID}/exposure-universe")
    world_card = response.json()["missing_worlds"][0]
    assert world_card["level"] == "partially_explored"
    assert world_card["level"] != "explored"  # one interaction alone never jumps straight to explored
