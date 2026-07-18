from fastapi import APIRouter, Depends

from aureon.api.deps import get_trend_repository
from aureon.domain.services.trend_view import build_future_skills_view, build_trend_dto
from aureon.services.supabase.repositories.trend_repository import TrendRepository
from aureon.shared.schemas import FutureSkillsResponse, TrendsResponse

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("", response_model=TrendsResponse)
async def list_trends(
    category: str | None = None,
    industry: str | None = None,
    region: str | None = None,
    trends: TrendRepository = Depends(get_trend_repository),
) -> TrendsResponse:
    """Global Trends' browse endpoint — always open, no gating. Industry/
    market-level growth patterns, deliberately distinct from any single
    career's own FutureLens narrative."""
    results = await trends.list_trends(category=category, industry=industry, region=region)
    return TrendsResponse(trends=[build_trend_dto(t) for t in results])


@router.get("/future-skills", response_model=FutureSkillsResponse)
async def get_future_skills(
    trends: TrendRepository = Depends(get_trend_repository),
) -> FutureSkillsResponse:
    """A real, deterministic aggregation of which skills are named across
    the most seeded trends — never a separately authored/stored ranking."""
    all_trends = await trends.list_trends()
    return FutureSkillsResponse(skills=build_future_skills_view(all_trends))
