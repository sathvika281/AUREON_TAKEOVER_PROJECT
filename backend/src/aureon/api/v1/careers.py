from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import (
    get_career_repository,
    get_company_repository,
    get_project_repository,
    get_skill_repository,
    get_student_profile_repository,
    get_trend_repository,
)
from aureon.domain.services.career_view import build_career_detail_dto, build_career_summary_dto
from aureon.domain.services.related_careers import find_related_careers
from aureon.domain.services.world_signal_alignment import compute_tag_alignment
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.company_repository import CompanyRepository
from aureon.services.supabase.repositories.project_repository import ProjectRepository
from aureon.services.supabase.repositories.skill_repository import SkillRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.services.supabase.repositories.trend_repository import TrendRepository
from aureon.shared.schemas import CareerDetailDTO, CareerSummaryDTO

router = APIRouter(prefix="/careers", tags=["careers"])

#: Same "strong trait" threshold Hidden Potential uses — keeps
#: personalization consistent across features.
STRONG_TRAIT_THRESHOLD = 0.5


def _career_tags(career) -> list[str]:
    return [career.industry, career.category, career.name]


@router.get("", response_model=list[CareerSummaryDTO])
async def list_careers(
    category: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    q: str | None = None,
    student_id: str | None = None,
    careers: CareerRepository = Depends(get_career_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> list[CareerSummaryDTO]:
    """Global Career Discovery's browse/search endpoint — always open, no
    confidence gating, since browsing the catalog itself needs no personal
    evidence (students know only a tiny fraction of careers). When
    ``student_id`` is given, results are *reordered* (never filtered —
    every career the filters/search matched is still returned) by real
    World Signal alignment, ties broken by the existing order."""
    results = await careers.list_careers(category=category, industry=industry, country=country, q=q)

    if student_id:
        profile = await profiles.get_or_create(student_id)
        world_signals = profile.discovery_onboarding.world_signals
        results = sorted(
            results, key=lambda c: compute_tag_alignment(_career_tags(c), world_signals), reverse=True
        )

    return [build_career_summary_dto(c) for c in results]


@router.get("/{career_id}", response_model=CareerDetailDTO)
async def get_career_detail(
    career_id: str,
    student_id: str | None = None,
    careers: CareerRepository = Depends(get_career_repository),
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    trends: TrendRepository = Depends(get_trend_repository),
    skills: SkillRepository = Depends(get_skill_repository),
    companies: CompanyRepository = Depends(get_company_repository),
    projects: ProjectRepository = Depends(get_project_repository),
) -> CareerDetailDTO:
    """Career Reality + Future Lens + Human Stories for one career, plus
    Explore Batch 1's Related Careers / Recommended Next Exploration /
    Related Trends. When ``student_id`` is given, stories are ordered by
    trait-tag overlap with the student's strong Career DNA traits —
    simple tag overlap, not embeddings, matching the "not vector
    similarity" philosophy."""
    career = await careers.get_career(career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")
    stories = await careers.list_stories_for_career(career_id)

    student_trait_tags: set[str] | None = None
    recommended_next_exploration = None
    if student_id:
        profile = await profiles.get_or_create(student_id)
        student_trait_tags = {
            trait
            for trait, signal in profile.career_dna.traits.items()
            if (signal.score or 0) >= STRONG_TRAIT_THRESHOLD
        }
        full_catalog = await careers.list_careers()
        related = find_related_careers(career, full_catalog)
        visited_career_ids = {e.career_id for e in profile.career_exploration_history}
        recommended_next_exploration = next(
            (c for c in related if c.id not in visited_career_ids), None
        )
    else:
        full_catalog = await careers.list_careers()
        related = find_related_careers(career, full_catalog)

    related_trends = await trends.list_trends(industry=career.industry)
    required_skills = await skills.list_by_ids(career.required_skill_ids)
    hiring_companies = await companies.list_by_ids(career.company_ids)
    related_projects = await projects.list_projects_for_career(career_id)

    return build_career_detail_dto(
        career, stories, student_trait_tags=student_trait_tags,
        related_careers=related, recommended_next_exploration=recommended_next_exploration,
        related_trends=related_trends, required_skills=required_skills,
        hiring_companies=hiring_companies, related_projects=related_projects,
    )
