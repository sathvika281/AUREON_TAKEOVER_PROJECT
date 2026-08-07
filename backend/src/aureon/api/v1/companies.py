from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_career_repository, get_company_repository
from aureon.domain.services.company_view import build_company_detail_view, build_company_dto
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.company_repository import CompanyRepository
from aureon.shared.schemas import CompaniesResponse, CompanyDetailResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=CompaniesResponse)
async def list_companies(
    industry: str | None = None,
    organization_kind: str | None = None,
    companies: CompanyRepository = Depends(get_company_repository),
) -> CompaniesResponse:
    """Company catalog browse endpoint — always open, no gating, same as
    every other knowledge-base catalog (Skills, Trends, Opportunities)."""
    results = await companies.list_companies(industry=industry, organization_kind=organization_kind)
    return CompaniesResponse(companies=[build_company_dto(c) for c in results])


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: str,
    companies: CompanyRepository = Depends(get_company_repository),
    careers: CareerRepository = Depends(get_career_repository),
) -> CompanyDetailResponse:
    company = await companies.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    careers_hiring_from_it = await careers.list_careers_hiring_from_company(company_id)
    return build_company_detail_view(company, careers_hiring_from_it)
