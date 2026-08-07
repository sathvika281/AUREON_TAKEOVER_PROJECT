from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_career_repository, get_skill_repository
from aureon.domain.services.skill_view import build_skill_detail_view, build_skill_dto
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.skill_repository import SkillRepository
from aureon.shared.schemas import SkillDetailResponse, SkillsResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=SkillsResponse)
async def list_skills(
    category: str | None = None,
    skills: SkillRepository = Depends(get_skill_repository),
) -> SkillsResponse:
    """Skill catalog browse endpoint — always open, no gating, same as
    every other knowledge-base catalog (Trends, Opportunities)."""
    results = await skills.list_skills(category=category)
    return SkillsResponse(skills=[build_skill_dto(s) for s in results])


@router.get("/{skill_id}", response_model=SkillDetailResponse)
async def get_skill(
    skill_id: str,
    skills: SkillRepository = Depends(get_skill_repository),
    careers: CareerRepository = Depends(get_career_repository),
) -> SkillDetailResponse:
    skill = await skills.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    careers_requiring_it = await careers.list_careers_requiring_skill(skill_id)
    return build_skill_detail_view(skill, careers_requiring_it)
