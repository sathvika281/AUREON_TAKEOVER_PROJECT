from datetime import datetime, timezone

import pytest

from aureon.api import deps
from aureon.domain.models.experiment import ExperimentCompletion, ExperimentEvidence
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"
NOW = datetime.now(timezone.utc)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)


def test_get_talents_is_empty_for_a_new_student(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/talents")

    assert response.status_code == 200
    assert response.json()["patterns"] == []


def test_get_talents_reflects_real_experiment_evidence(api_client):
    client, fake_profiles = api_client
    profile = fake_profiles._profiles[STUDENT_ID]
    for _ in range(2):
        profile.career_experiments.append(
            ExperimentCompletion(
                id="c1", experiment_id="exp_1", experiment_title="Debug a Tiny Bug", related_world="AI",
                target_traits=["persistence"], completed_at=NOW, evidence=ExperimentEvidence(persistence=True),
            )
        )

    response = client.get(f"/v1/students/{STUDENT_ID}/talents")

    assert response.status_code == 200
    patterns = response.json()["patterns"]
    persistence = next(p for p in patterns if p["talent"] == "persistence")
    assert persistence["tier"] == "emerging"
    assert persistence["explanation"]
    assert len(persistence["evidence"]) == 2
