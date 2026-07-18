from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.api.deps import get_student_profile_repository, require_own_profile
from aureon.agents.specialized.opportunity.providers.registry import fetch_all_safely
from aureon.domain.services.opportunity_equality import find_equality_opportunities
from aureon.services.foundation.career_memory.service import (
    get_career_memory_snapshot,
    record_opportunity_entry,
)
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import (
    OpportunityEqualityInteractionRequest,
    OpportunityEqualityInteractionResponse,
    OpportunityEqualityRecommendationDTO,
    OpportunityEqualityResponse,
    OpportunitySummaryDTO,
)

router = APIRouter(prefix="/students", tags=["opportunity-equality"], dependencies=[Depends(require_own_profile)])


def _opportunity_summary(opportunity) -> OpportunitySummaryDTO:
    return OpportunitySummaryDTO(
        id=opportunity.id, title=opportunity.title, category=opportunity.category,
        organization=opportunity.organization, description=opportunity.description,
        location=opportunity.location, is_remote=opportunity.is_remote,
        application_deadline=opportunity.application_deadline, official_link=opportunity.official_link,
    )


@router.get("/{student_id}/opportunity-equality", response_model=OpportunityEqualityResponse)
async def get_opportunity_equality(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> OpportunityEqualityResponse:
    """"These are opportunities you are least likely to discover on
    your own" — never "here are today's opportunities." Reuses
    Opportunity Hub's existing catalog/scoring wholesale; the only new
    dimension is Exposure Gap Detection, layered alongside, never
    mutating Opportunity Hub's own fit ranking."""
    profile = await profiles.get_or_create(student_id)
    memory = get_career_memory_snapshot(profile)
    opportunities = await fetch_all_safely()

    recommendations = find_equality_opportunities(
        profile, memory, opportunities, now=datetime.now(timezone.utc)
    )

    return OpportunityEqualityResponse(
        recommendations=[
            OpportunityEqualityRecommendationDTO(
                opportunity=_opportunity_summary(r.opportunity),
                readiness_label=r.fit.readiness_label,
                likelihood_of_self_discovery=r.exposure_gap.likelihood_of_self_discovery,
                why_shown=r.exposure_gap.why_shown,
                contributing_factors=r.exposure_gap.contributing_factors,
            )
            for r in recommendations
        ]
    )


@router.post("/{student_id}/opportunity-equality/interact", response_model=OpportunityEqualityInteractionResponse)
async def record_opportunity_equality_interaction(
    student_id: str,
    body: OpportunityEqualityInteractionRequest,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> OpportunityEqualityInteractionResponse:
    """Reuses the exact same real interaction log Opportunity Hub itself
    writes to (`OpportunitiesMemory.entries`) — never a parallel log."""
    profile = await profiles.get_or_create(student_id)
    opportunities = await fetch_all_safely()
    opportunity = next((o for o in opportunities if o.id == body.opportunity_id), None)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    record_opportunity_entry(
        profile, interaction=body.interaction, category=opportunity.category, ref_id=opportunity.id,
        opportunity_version=opportunity.version, title=opportunity.title, now=datetime.now(timezone.utc),
    )
    await profiles.save(profile)
    return OpportunityEqualityInteractionResponse(recorded=True)
