import pytest

from aureon.api import deps
from aureon.domain.models.entrance_exam import EntranceExam
from aureon.domain.models.institution import Institution
from aureon.main import app


class _FakeInstitutionRepository:
    def __init__(self, institution: Institution):
        self._institution = institution

    async def get_institution(self, institution_id):
        return self._institution if institution_id == self._institution.id else None

    async def list_research_labs(self, institution_id):
        return []

    async def list_student_organizations(self, institution_id):
        return []

    async def list_academic_programs(self, institution_id):
        return []

    async def list_innovation_centers(self, institution_id):
        return []

    async def list_faculty_highlights(self, institution_id):
        return []

    async def list_student_ambassadors(self, institution_id):
        return []

    async def list_student_projects(self, institution_id):
        return []

    async def list_internship_opportunities(self, institution_id):
        return []


class _FakeCareerEventRepository:
    async def list_career_events(self, **_kwargs):
        return []


class _FakeEntranceExamRepository:
    def __init__(self, exams):
        self._exams = exams

    async def list_for_institution(self, institution_id):
        return [x for x in self._exams if institution_id in x.accepted_institution_ids]


def _institution(**overrides) -> Institution:
    defaults: dict = dict(
        id="inst_1", name="Test University", country="Testland", city="Test City",
        research_culture="x", innovation_ecosystem="x", industry_collaboration="x",
        placements="x", learning_environment="x",
        campus_life_and_culture="A real, honest campus life description.",
        fees_summary="A real, hedged fee summary.",
        scholarships_summary="A real, hedged scholarship summary.",
    )
    defaults.update(overrides)
    return Institution(**defaults)


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    exam = EntranceExam(
        id="exam_1", name="Test Entrance Exam", description="x", preparation_guidance="x",
        typical_timeline="x", accepted_institution_ids=["inst_1"],
    )
    app.dependency_overrides[deps.get_institution_repository] = lambda: _FakeInstitutionRepository(_institution())
    app.dependency_overrides[deps.get_career_event_repository] = lambda: _FakeCareerEventRepository()
    app.dependency_overrides[deps.get_entrance_exam_repository] = lambda: _FakeEntranceExamRepository([exam])
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_institution_repository, None)
        app.dependency_overrides.pop(deps.get_career_event_repository, None)
        app.dependency_overrides.pop(deps.get_entrance_exam_repository, None)


def test_institution_detail_merges_entrance_exams_no_separate_route(api_client):
    response = api_client.get("/v1/institutions/inst_1")
    assert response.status_code == 200
    body = response.json()
    assert body["entrance_exams"][0]["id"] == "exam_1"
    assert body["campus_life_and_culture"] == "A real, honest campus life description."
    assert body["fees_summary"]
    assert body["scholarships_summary"]


def test_institution_not_found_returns_404(api_client):
    response = api_client.get("/v1/institutions/does_not_exist")
    assert response.status_code == 404
