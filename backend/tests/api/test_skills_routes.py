import pytest

from aureon.api import deps
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.skill import Skill
from aureon.main import app

_REALITY = CareerReality(
    daily_work="x", work_environment="x", collaboration_level="x", creativity_level="x",
    research_intensity="x", learning_curve="x", travel="x", remote_possibility="x",
    stress_factors="x", typical_challenges="x", misconceptions="x", long_term_growth="x",
    required_education="x",
)
_FUTURE = FutureLens(
    ai_impact="x", automation_risk="x", demand_2030="x", demand_2035="x", demand_2040="x",
    emerging_opportunities="x", timeline_narrative="x",
)


class _FakeSkillRepository:
    def __init__(self, skills):
        self._skills = skills

    async def list_skills(self, *, category=None):
        results = self._skills
        if category:
            results = [s for s in results if s.category == category]
        return results

    async def get_skill(self, skill_id):
        return next((s for s in self._skills if s.id == skill_id), None)

    async def list_by_ids(self, skill_ids):
        return [s for s in self._skills if s.id in skill_ids]


class _FakeCareerRepository:
    def __init__(self, careers):
        self._careers = careers

    async def list_careers(self, **_kwargs):
        return self._careers

    async def list_careers_requiring_skill(self, skill_id):
        return [c for c in self._careers if skill_id in c.required_skill_ids]


def _skill(**overrides) -> Skill:
    defaults: dict = dict(id="programming", name="Programming", category="technical", description="x")
    defaults.update(overrides)
    return Skill(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
        required_skill_ids=["programming"],
    )
    defaults.update(overrides)
    return Career(**defaults)


@pytest.fixture
def client_with_skills():
    from fastapi.testclient import TestClient

    fake_skills = _FakeSkillRepository(
        [_skill(id="programming"), _skill(id="stakeholder_communication", category="soft_skill")]
    )
    fake_careers = _FakeCareerRepository([_career()])
    app.dependency_overrides[deps.get_skill_repository] = lambda: fake_skills
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_skill_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)


def test_list_skills_returns_all_by_default(client_with_skills):
    response = client_with_skills.get("/v1/skills")
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 2


def test_list_skills_filters_by_category(client_with_skills):
    response = client_with_skills.get("/v1/skills", params={"category": "soft_skill"})
    assert response.status_code == 200
    skills = response.json()["skills"]
    assert len(skills) == 1
    assert skills[0]["id"] == "stakeholder_communication"


def test_get_skill_returns_real_requiring_careers(client_with_skills):
    response = client_with_skills.get("/v1/skills/programming")
    assert response.status_code == 200
    body = response.json()
    assert body["skill"]["id"] == "programming"
    assert len(body["careers_requiring_it"]) == 1
    assert body["careers_requiring_it"][0]["id"] == "genomics_data_scientist"


def test_get_skill_never_fabricates_requiring_careers(client_with_skills):
    response = client_with_skills.get("/v1/skills/stakeholder_communication")
    assert response.status_code == 200
    assert response.json()["careers_requiring_it"] == []


def test_get_unknown_skill_returns_404(client_with_skills):
    response = client_with_skills.get("/v1/skills/does-not-exist")
    assert response.status_code == 404
