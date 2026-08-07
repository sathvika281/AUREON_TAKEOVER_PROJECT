"""Responsibility: presentation mapping + composition for the Company
Knowledge Base. Owns: ``build_company_dto``, ``build_company_detail_view``.
Mirrors ``skill_view.py`` exactly — the pattern proven once in Sprint 1,
reused here rather than reinvented. Consumed by: ``api/v1/companies.py``.
"""

from aureon.domain.models.career import Career
from aureon.domain.models.company import Company
from aureon.shared.schemas import CareerSummaryDTO, CompanyDetailResponse, CompanyDTO


def build_company_dto(company: Company) -> CompanyDTO:
    return CompanyDTO(
        id=company.id,
        name=company.name,
        organization_kind=company.organization_kind,
        industry=company.industry,
        size_category=company.size_category,
        what_they_do=company.what_they_do,
        logo_url=company.logo_url,
        hiring_focus_areas=company.hiring_focus_areas,
        notable_for=company.notable_for,
    )


def build_company_detail_view(company: Company, careers_hiring_from_it: list[Career]) -> CompanyDetailResponse:
    """Composes a Company with the real careers that hire from it — never
    a stored/duplicated list, always resolved live from Career's own
    ``company_ids`` edge (see CareerRepository.list_careers_hiring_from_company)."""
    return CompanyDetailResponse(
        company=build_company_dto(company),
        careers_hiring_from_it=[
            CareerSummaryDTO(
                id=c.id, name=c.name, category=c.category, industry=c.industry,
                countries=c.countries, one_liner=c.one_liner, trait_tags=c.trait_tags,
            )
            for c in careers_hiring_from_it
        ],
    )
