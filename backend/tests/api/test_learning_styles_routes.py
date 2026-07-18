import pytest

from aureon.api import deps
from aureon.domain.models.career_dna import TraitSignal
from aureon.domain.models.learning_style import LearningStyle
from aureon.domain.models.student_profile import StudentProfile
from aureon.main import app
from tests.fakes import FakeStudentProfileRepository

STUDENT_ID = "s1"


def _style(**overrides) -> LearningStyle:
    defaults = dict(id="style_visual", name="Visual", description="d", keywords=["visual", "diagram"])
    defaults.update(overrides)
    return LearningStyle(**defaults)


class _FakeLearningStyleRepository:
    def __init__(self, styles):
        self._styles = styles

    async def list_styles(self):
        return self._styles


class _FakeExperimentRepository:
    async def list_experiments(self):
        return []


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    fake_profiles = FakeStudentProfileRepository({STUDENT_ID: StudentProfile(student_id=STUDENT_ID)})
    app.dependency_overrides[deps.get_current_user_id] = lambda: STUDENT_ID
    app.dependency_overrides[deps.get_student_profile_repository] = lambda: fake_profiles
    app.dependency_overrides[deps.get_learning_style_repository] = lambda: _FakeLearningStyleRepository([_style()])
    app.dependency_overrides[deps.get_experiment_repository] = lambda: _FakeExperimentRepository()
    try:
        yield TestClient(app), fake_profiles
    finally:
        app.dependency_overrides.pop(deps.get_current_user_id, None)
        app.dependency_overrides.pop(deps.get_student_profile_repository, None)
        app.dependency_overrides.pop(deps.get_learning_style_repository, None)
        app.dependency_overrides.pop(deps.get_experiment_repository, None)


def test_get_learning_styles_is_empty_for_a_new_student(api_client):
    client, _ = api_client
    response = client.get(f"/v1/students/{STUDENT_ID}/learning-styles")

    assert response.status_code == 200
    assert response.json()["patterns"] == []


def test_get_learning_styles_reflects_real_career_dna_signal(api_client):
    client, fake_profiles = api_client
    profile = fake_profiles._profiles[STUDENT_ID]
    profile.career_dna.traits["learning_style"] = TraitSignal(score=None, summary="Prefers visual diagrams")

    response = client.get(f"/v1/students/{STUDENT_ID}/learning-styles")

    body = response.json()
    assert len(body["patterns"]) == 1
    assert body["patterns"][0]["style"]["name"] == "Visual"
    assert body["patterns"][0]["tier"] == "still_emerging"
