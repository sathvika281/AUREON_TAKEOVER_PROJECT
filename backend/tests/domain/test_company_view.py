from aureon.domain.models.career import Career, CareerReality, FutureLens
from aureon.domain.models.company import Company
from aureon.domain.services.company_view import build_company_detail_view, build_company_dto

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


def _company(**overrides) -> Company:
    defaults: dict = dict(
        id="google", name="Google", organization_kind="company", industry="technology",
        what_they_do="A technology company known for search and cloud computing.",
    )
    defaults.update(overrides)
    return Company(**defaults)


def _career(**overrides) -> Career:
    defaults: dict = dict(
        id="genomics_data_scientist", name="Genomics Data Scientist", category="emerging",
        industry="biotechnology", one_liner="x", reality=_REALITY, future_lens=_FUTURE,
    )
    defaults.update(overrides)
    return Career(**defaults)


def test_build_company_dto_maps_all_fields():
    company = _company(
        size_category="enterprise", logo_url="https://logo.clearbit.com/google.com",
        hiring_focus_areas=["software engineering"], notable_for="strong new-grad mentorship",
    )
    dto = build_company_dto(company)
    assert dto.id == "google"
    assert dto.organization_kind == "company"
    assert dto.size_category == "enterprise"
    assert dto.logo_url == "https://logo.clearbit.com/google.com"
    assert dto.hiring_focus_areas == ["software engineering"]


def test_build_company_dto_honestly_leaves_size_category_none_for_nonprofits():
    # A nonprofit/government org never gets a forced startup/mid/enterprise label.
    who = _company(id="who", name="World Health Organization", organization_kind="nonprofit", size_category=None)
    dto = build_company_dto(who)
    assert dto.size_category is None


def test_company_detail_view_composes_real_hiring_careers():
    company = _company()
    career = _career()
    view = build_company_detail_view(company, [career])
    assert view.company.id == "google"
    assert len(view.careers_hiring_from_it) == 1
    assert view.careers_hiring_from_it[0].id == "genomics_data_scientist"


def test_company_detail_view_never_fabricates_hiring_careers():
    # No hiring careers passed in -> honestly empty, never guessed.
    view = build_company_detail_view(_company(), [])
    assert view.careers_hiring_from_it == []
