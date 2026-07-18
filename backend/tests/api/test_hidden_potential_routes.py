from datetime import datetime, timezone

import pytest

from aureon.api import deps
from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"
NOW = datetime.now(timezone.utc)


class _FakeExperimentRepository:
    async def list_experiments(self):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_experiment_repository] = lambda: _FakeExperimentRepository()
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_experiment_repository, None)


def test_get_hidden_potential_is_empty_for_a_new_student(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/hidden-potential")

    assert response.status_code == 200
    body = response.json()
    assert body["hidden_patterns"] == []
    assert body["strengths"] == {"emerging": [], "growing": [], "consistently_observed": []}
    assert body["suggested_experience"] is None
    assert body["discovery_statistics"]["traits_tracked"] == 0


def test_get_hidden_potential_reflects_real_career_dna(api_client):
    client, fake_profiles = api_client
    profile = fake_profiles._profiles[STUDENT_ID]
    profile.career_dna.traits["analytical_thinking"] = TraitSignal(score=0.6, summary="s")
    profile.career_dna.traits["creativity"] = TraitSignal(score=0.6, summary="s")

    response = client.get(f"/v1/students/{STUDENT_ID}/hidden-potential")

    assert response.status_code == 200
    body = response.json()
    assert len(body["hidden_patterns"]) == 1
    assert body["discovery_statistics"]["traits_tracked"] == 2
