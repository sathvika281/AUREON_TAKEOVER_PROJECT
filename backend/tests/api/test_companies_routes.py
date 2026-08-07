import pytest

from aureon.api import deps
from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.company import Company
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


class _FakeCompanyRepository:
    def __init__(self, companies):
        self._companies = companies

    async def list_companies(self, *, industry=None, organization_kind=None):
        results = self._companies
        if industry:
            results = [c for c in results if c.industry == industry]
        if organization_kind:
            results = [c for c in results if c.organization_kind == organization_kind]
        return results

    async def get_company(self, company_id):
        return next((c for c in self._companies if c.id == company_id), None)

    async def list_by_ids(self, company_ids):
        return [c for c in self._companies if c.id in company_ids]


class _FakeCareerRepository:
    def __init__(self, careers):
        self._careers = careers

    async def list_careers(self, **_kwargs):
        return self._careers

    async def list_careers_hiring_from_company(self, company_id):
        return [c for c in self._careers if company_id in c.company_ids]


def _company(**overrides) -> Company:
    defaults: dict = dict(
        id="google", name="Google", organization_kind="company", industry="technology",
        what_they_do="x",
    )
    defaults.update(overrides)
    return Company(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
        company_ids=["google"],
    )
    defaults.update(overrides)
    return Career(**defaults)


@pytest.fixture
def client_with_companies():
    from fastapi.testclient import TestClient

    fake_companies = _FakeCompanyRepository(
        [_company(id="google"), _company(id="who", name="World Health Organization", organization_kind="nonprofit", industry="public health & policy")]
    )
    fake_careers = _FakeCareerRepository([_career()])
    app.dependency_overrides[deps.get_company_repository] = lambda: fake_companies
    app.dependency_overrides[deps.get_career_repository] = lambda: fake_careers
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(deps.get_company_repository, None)
        app.dependency_overrides.pop(deps.get_career_repository, None)


def test_list_companies_returns_all_by_default(client_with_companies):
    response = client_with_companies.get("/v1/companies")
    assert response.status_code == 200
    assert len(response.json()["companies"]) == 2


def test_list_companies_filters_by_organization_kind(client_with_companies):
    response = client_with_companies.get("/v1/companies", params={"organization_kind": "nonprofit"})
    assert response.status_code == 200
    companies = response.json()["companies"]
    assert len(companies) == 1
    assert companies[0]["id"] == "who"


def test_get_company_returns_real_hiring_careers(client_with_companies):
    response = client_with_companies.get("/v1/companies/google")
    assert response.status_code == 200
    body = response.json()
    assert body["company"]["id"] == "google"
    assert len(body["careers_hiring_from_it"]) == 1
    assert body["careers_hiring_from_it"][0]["id"] == "genomics_data_scientist"


def test_get_company_never_fabricates_hiring_careers(client_with_companies):
    response = client_with_companies.get("/v1/companies/who")
    assert response.status_code == 200
    assert response.json()["careers_hiring_from_it"] == []


def test_get_unknown_company_returns_404(client_with_companies):
    response = client_with_companies.get("/v1/companies/does-not-exist")
    assert response.status_code == 404
