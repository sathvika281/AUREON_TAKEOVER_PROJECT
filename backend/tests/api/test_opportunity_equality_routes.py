import pytest

from aureon.api import deps
from aureon.api.v1 import opportunity_equality as opportunity_equality_route
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.agents.opportunity._factories import make_opportunity
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"
OPPORTUNITY = make_opportunity(id="opp_1", min_academic_level="any", countries=[])


@pytest.fixture
def api_client(monkeypatch):
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})

    async def _fake_fetch_all_safely():
        return [OPPORTUNITY]

    monkeypatch.setattr(opportunity_equality_route, "fetch_all_safely", _fake_fetch_all_safely)
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)


def test_get_opportunity_equality_returns_real_recommendation_with_why_shown(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/opportunity-equality")

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 1
    rec = recommendations[0]
    assert rec["opportunity"]["id"] == "opp_1"
    assert rec["why_shown"]
    assert rec["likelihood_of_self_discovery"] in {"low", "medium", "high"}


def test_interact_records_real_entry_via_shared_opportunity_hub_log(api_client):
    client, fake_profiles = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/opportunity-equality/interact",
        json={"opportunity_id": "opp_1", "interaction": "saved"},
    )

    assert response.status_code == 200
    assert response.json()["recorded"] is True
    saved = fake_profiles.saved[-1]
    entry = saved.foundation_memory.opportunities.entries[0]
    assert entry.ref_id == "opp_1"
    assert entry.interaction == "saved"


def test_interact_with_unknown_opportunity_404s(api_client):
    client, _ = api_client
    response = client.post(
        f"/v1/students/{STUDENT_ID}/opportunity-equality/interact",
        json={"opportunity_id": "does_not_exist", "interaction": "viewed"},
    )
    assert response.status_code == 404
