from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_career_repository, get_student_profile_repository
from aureon.domain.services.career_view import build_career_detail_dto, build_career_summary_dto
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import CareerDetailDTO, CareerSummaryDTO

router = APIRouter(prefix="/careers", tags=["careers"])

#: Same "strong trait" threshold Hidden Potential uses — keeps
#: personalization consistent across features.
STRONG_TRAIT_THRESHOLD = 0.5


@router.get("", response_model=list[CareerSummaryDTO])
async def list_careers(
    category: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    q: str | None = None,
    careers: CareerRepository = Depends(get_career_repository),
) -> list[CareerSummaryDTO]:
    """Global Career Discovery's browse/search endpoint — always open, no
    confidence gating, since browsing the catalog itself needs no personal
    evidence (students know only a tiny fraction of careers)."""
    results = await careers.list_careers(category=category, industry=industry, country=country, q=q)
    return [build_career_summary_dto(c) for c in results]


@router.get("/{career_id}", response_model=CareerDetailDTO)
async def get_career_detail(
    career_id: str,
    student_id: str | None = None,
    careers: CareerRepository = Depends(get_career_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerDetailDTO:
    """Career Reality + Future Lens + Human Stories for one career. When
    ``student_id`` is given, stories are ordered by trait-tag overlap with
    the student's strong Career DNA traits — simple tag overlap, not
    embeddings, matching the "not vector similarity" philosophy."""
    career = await careers.get_career(career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")
    stories = await careers.list_stories_for_career(career_id)

    student_trait_tags: set[str] | None = None
    if student_id:
        profile = await profiles.get_or_create(student_id)
        student_trait_tags = {
            trait
            for trait, signal in profile.career_dna.traits.items()
            if (signal.score or 0) >= STRONG_TRAIT_THRESHOLD
        }

    return build_career_detail_dto(career, stories, student_trait_tags=student_trait_tags)
