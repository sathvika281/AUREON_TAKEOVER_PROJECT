from datetime import datetime, timezone

import pytest

from aureon.api import deps
from aureon.domain.models.experiment import Experiment
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"
NOW = datetime.now(timezone.utc)


def _experiment(**overrides) -> Experiment:
    defaults = dict(
        id="exp_1", title="Debug a Tiny Bug", category="debug_code", description="d", instructions="i",
        estimated_minutes=10, age_appropriate_note="note", related_world="AI",
        target_traits=["analytical_thinking", "persistence"], reflection_prompt="p", created_at=NOW, updated_at=NOW,
    )
    defaults.update(overrides)
    return Experiment(**defaults)


def _mission(**overrides) -> LifeMission:
    defaults = dict(
        id="mission_climate", name="Solve Climate Problems", description="d",
        related_tags=["climate", "sustainability"],
    )
    defaults.update(overrides)
    return LifeMission(**defaults)


class _FakeExperimentRepository:
    def __init__(self, experiments):
        self._experiments = {e.id: e for e in experiments}

    async def list_experiments(self):
        return list(self._experiments.values())

    async def get_experiment(self, experiment_id):
        return self._experiments.get(experiment_id)


class _FakeLifeMissionRepository:
    def __init__(self, missions):
        self._missions = list(missions)

    async def list_missions(self):
        return self._missions


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    fake_experiments = _FakeExperimentRepository([_experiment()])
    fake_missions = _FakeLifeMissionRepository([_mission()])
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_experiment_repository] = lambda: fake_experiments
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: fake_missions
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_experiment_repository, None)
        app.dependency_overrides.pop(deps.get_life_mission_repository, None)


def test_list_experiments_returns_catalog_and_empty_completions(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/experiments")

    assert response.status_code == 200
    body = response.json()
    assert len(body["experiments"]) == 1
    assert body["experiments"][0]["id"] == "exp_1"
    assert body["completed_experiment_ids"] == []


def test_complete_experiment_records_and_returns_completion(api_client):
    client, fake_profiles = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/experiments/exp_1/complete",
        json={"enjoyment": True, "persistence": True, "reflection": "That was tricky but fun."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["experiment_id"] == "exp_1"
    assert body["evidence"]["enjoyment"] is True
    assert body["evidence"]["reflection"] == "That was tricky but fun."

    saved = fake_profiles.saved[-1]
    assert len(saved.career_experiments) == 1
    ai_signal = next(s for s in saved.discovery_onboarding.world_signals if s.world == "AI")
    assert ai_signal.confidence > 0.3


def test_completed_experiment_appears_in_completed_ids(api_client):
    client, _ = api_client
    client.post(f"/v1/students/{STUDENT_ID}/experiments/exp_1/complete", json={})

    response = client.get(f"/v1/students/{STUDENT_ID}/experiments")

    assert response.json()["completed_experiment_ids"] == ["exp_1"]


def test_complete_unknown_experiment_returns_404(api_client):
    client, _ = api_client
    response = client.post(f"/v1/students/{STUDENT_ID}/experiments/nope/complete", json={})

    assert response.status_code == 404


def test_experience_lab_view_groups_career_experience_with_no_missions(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/experience-lab")

    assert response.status_code == 200
    body = response.json()
    assert [e["id"] for e in body["career_experiences"]] == ["exp_1"]
    assert body["mission_experiences"] == []
    assert body["emerging_missions"] == []
    assert body["completed"] == []


@pytest.fixture
def mission_linked_client():
    from fastapi.testclient import TestClient

    mission_experiment = _experiment(
        id="exp_climate", title="Analyze a climate problem", related_world="Business",
        target_traits=["analytical_thinking"], related_life_mission_ids=["mission_climate"],
    )
    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    fake_experiments = _FakeExperimentRepository([mission_experiment])
    fake_missions = _FakeLifeMissionRepository([_mission()])
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_experiment_repository] = lambda: fake_experiments
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: fake_missions
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_experiment_repository, None)
        app.dependency_overrides.pop(deps.get_life_mission_repository, None)


def test_experience_lab_view_shows_mission_experience_before_completion(mission_linked_client):
    client, _ = mission_linked_client
    response = client.get(f"/v1/students/{STUDENT_ID}/experience-lab")

    assert response.status_code == 200
    body = response.json()
    assert [e["id"] for e in body["mission_experiences"]] == ["exp_climate"]
    assert body["career_experiences"] == []
    # No evidence yet — the mission must not appear as emerging.
    assert body["emerging_missions"] == []


def test_completing_mission_experience_with_genuine_signal_surfaces_it_as_emerging(mission_linked_client):
    client, _ = mission_linked_client
    complete = client.post(
        f"/v1/students/{STUDENT_ID}/experiments/exp_climate/complete",
        json={"curiosity": True, "reflection": "This made me think about my own energy use."},
    )
    assert complete.status_code == 200

    response = client.get(f"/v1/students/{STUDENT_ID}/experience-lab")
    body = response.json()

    assert len(body["emerging_missions"]) == 1
    emerging = body["emerging_missions"][0]
    assert emerging["mission"]["id"] == "mission_climate"
    assert emerging["tier"] in ("still_emerging", "growing", "strong")
    assert any(e["source"] == "experiment" for e in emerging["evidence"])
    # Already completed — must not be re-suggested as its own next step.
    assert emerging["suggested_experience"] is None


def test_completing_mission_experience_without_genuine_signal_does_not_inflate_any_mission(mission_linked_client):
    client, _ = mission_linked_client
    complete = client.post(f"/v1/students/{STUDENT_ID}/experiments/exp_climate/complete", json={})
    assert complete.status_code == 200

    response = client.get(f"/v1/students/{STUDENT_ID}/experience-lab")
    body = response.json()

    assert body["emerging_missions"] == []
