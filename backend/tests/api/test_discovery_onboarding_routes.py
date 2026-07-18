import pytest

from aureon.api import deps
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


class _FakeExperimentRepository:
    """Discover Batch 2 — the progressive-discovery GET route now also
    fetches the Experiment catalog. Empty by default: these tests only
    assert on onboarding/checkin behavior, not suggested_experiment."""

    async def list_experiments(self):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_repo = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_repo
    app.dependency_overrides[deps.get_experiment_repository] = lambda: _FakeExperimentRepository()
    try:
        yield TestClient(app), fake_repo
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_experiment_repository, None)


def test_progressive_discovery_before_onboarding_shows_incomplete(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/progressive-discovery")

    assert response.status_code == 200
    body = response.json()
    assert body["onboarding_completed"] is False
    assert body["pending_curiosity_checkin"] is None
    assert body["orbit_status"]["current_orbit"]  # a real stage, always present


def test_submit_onboarding_persists_and_returns_fresh_state(api_client):
    client, fake_repo = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/onboarding",
        json={
            "name": "Alex", "age": 17, "stage": "College", "location_state": "Karnataka",
            "location_city": "Bengaluru", "preferred_language": "English",
            "current_situation": "few_careers", "worlds": ["AI", "Space"], "worlds_unsure": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["onboarding_completed"] is True
    assert body["pending_curiosity_checkin"]["world"] == "AI"
    assert len(body["world_signals"]) == 2

    saved = fake_repo.saved[-1]
    assert saved.discovery_onboarding.completed is True
    assert saved.foundation_memory.identity.academic_level == "undergraduate"


def test_answer_curiosity_checkin_advances_the_queue(api_client):
    client, _ = api_client
    client.post(
        f"/v1/students/{STUDENT_ID}/onboarding",
        json={
            "name": "Alex", "age": 17, "stage": "College", "location_state": "Karnataka",
            "location_city": "Bengaluru", "preferred_language": "English",
            "current_situation": "few_careers", "worlds": ["AI", "Space"], "worlds_unsure": False,
        },
    )

    response = client.post(
        f"/v1/students/{STUDENT_ID}/curiosity-checkins/answer",
        json={"world": "AI", "chosen_options": ["Python"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pending_curiosity_checkin"]["world"] == "Space"
    ai_signal = next(s for s in body["world_signals"] if s["world"] == "AI")
    assert ai_signal["confidence"] == 0.5
    assert ai_signal["status"] == "reinforced"


def test_progressive_discovery_get_reflects_prior_onboarding(api_client):
    client, _ = api_client
    client.post(
        f"/v1/students/{STUDENT_ID}/onboarding",
        json={
            "name": None, "age": None, "stage": None, "location_state": None, "location_city": None,
            "preferred_language": None, "current_situation": "no_idea", "worlds": [], "worlds_unsure": True,
        },
    )

    response = client.get(f"/v1/students/{STUDENT_ID}/progressive-discovery")

    assert response.status_code == 200
    assert response.json()["onboarding_completed"] is True
