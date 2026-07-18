import pytest

from aureon.api import deps
from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.life_mission import LifeMission
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


def _mission(**overrides) -> LifeMission:
    defaults = dict(
        id="mission_climate", name="Solve Climate Problems", description="d",
        related_tags=["climate"],
    )
    defaults.update(overrides)
    return LifeMission(**defaults)


class _FakeLifeMissionRepository:
    def __init__(self, missions):
        self._missions = missions

    async def list_missions(self):
        return self._missions


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_life_mission_repository] = lambda: _FakeLifeMissionRepository([_mission()])
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_life_mission_repository, None)


def test_get_life_missions_puts_zero_evidence_mission_in_other_missions(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/life-missions")

    assert response.status_code == 200
    body = response.json()
    assert body["resonances"] == []
    assert len(body["other_missions"]) == 1
    assert body["other_missions"][0]["name"] == "Solve Climate Problems"


def test_get_life_missions_reflects_real_evidence(api_client):
    client, fake_profiles = api_client
    profile = fake_profiles._profiles[STUDENT_ID]
    profile.career_dna.traits["curiosity"] = TraitSignal(score=0.6, summary="Climate-focused curiosity.")

    response = client.get(f"/v1/students/{STUDENT_ID}/life-missions")

    body = response.json()
    assert len(body["resonances"]) == 1
    assert body["resonances"][0]["tier"] == "still_emerging"
    assert body["other_missions"] == []
