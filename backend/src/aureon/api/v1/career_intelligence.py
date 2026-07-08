from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from aureon.agents.specialized.career_intelligence.candidates import (
    MIN_TRAITS_FOR_ANALYSIS,
    upsert_candidates,
)
from aureon.agents.specialized.career_intelligence.reasoning import analyze_careers
from aureon.api.deps import (
    get_career_repository,
    get_institution_repository,
    get_student_profile_repository,
    require_own_profile,
)
from aureon.domain.services.decision_memory import remove_candidate, shortlist_candidate
from aureon.domain.services.match_recommendations import (
    top_active_institution_names,
    top_active_mentor_names,
)
from aureon.domain.services.profile_view import build_career_candidate_dtos
from aureon.services.llm.factory import get_llm_client
from aureon.services.supabase.repositories.career_repository import CareerRepository
from aureon.services.supabase.repositories.institution_repository import InstitutionRepository
from aureon.services.supabase.repositories.student_profile_repository import (
    StudentProfileRepository,
)
from aureon.shared.schemas import CareerCandidatesResponse

router = APIRouter(prefix="/students", tags=["career-intelligence"], dependencies=[Depends(require_own_profile)])


async def _partner_institution_ids(institutions: InstitutionRepository) -> set[str]:
    partners = await institutions.list_institutions(is_partner=True)
    return {i.id for i in partners}


@router.post("/{student_id}/career-candidates/analyze", response_model=CareerCandidatesResponse)
async def analyze_career_candidates(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    careers: CareerRepository = Depends(get_career_repository),
    institutions: InstitutionRepository = Depends(get_institution_repository),
) -> CareerCandidatesResponse:
    """The primary trigger for Career Intelligence — "conversation
    optional": bypasses the LangGraph planner entirely since this isn't
    conversational turn-taking, calling the same ``analyze_careers``
    reasoning function the conversational agent uses.
    """
    profile = await profiles.get_or_create(student_id)

    if len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS:
        return CareerCandidatesResponse(
            candidates=build_career_candidate_dtos(profile),
            insufficient_evidence=True,
            insufficient_evidence_reason=(
                "Not enough evidence yet — keep exploring in Identity Discovery so "
                "Aureon has more of your Career DNA to reason from."
            ),
        )

    career_list = await careers.list_careers()
    llm = get_llm_client()
    output = await analyze_careers(profile, career_list, llm=llm)

    if not output.insufficient_evidence:
        # Always runs even when `candidates` is empty this round — see
        # CareerIntelligenceAgent.run for why this must not be skipped.
        careers_by_id = {c.id: c.name for c in career_list}
        now = datetime.now(timezone.utc)
        upsert_candidates(profile, output.candidates, careers_by_id, now)
        profile.updated_at = now
        await profiles.save(profile)

    partner_ids = await _partner_institution_ids(institutions)
    return CareerCandidatesResponse(
        candidates=build_career_candidate_dtos(profile),
        insufficient_evidence=output.insufficient_evidence,
        insufficient_evidence_reason=output.insufficient_evidence_reason,
        recommended_colleges=top_active_institution_names(profile, partner_ids=partner_ids),
        recommended_experts=top_active_mentor_names(profile),
    )


@router.get("/{student_id}/career-candidates", response_model=CareerCandidatesResponse)
async def get_career_candidates(
    student_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
    institutions: InstitutionRepository = Depends(get_institution_repository),
) -> CareerCandidatesResponse:
    """Reads persisted candidates only — same "survives refresh/new
    device" pattern as ``GET .../discovery-profile``, no LLM call."""
    profile = await profiles.get_or_create(student_id)
    partner_ids = await _partner_institution_ids(institutions)
    return CareerCandidatesResponse(
        candidates=build_career_candidate_dtos(profile),
        insufficient_evidence=len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS,
        insufficient_evidence_reason=None,
        recommended_colleges=top_active_institution_names(profile, partner_ids=partner_ids),
        recommended_experts=top_active_mentor_names(profile),
    )


@router.post("/{student_id}/career-candidates/{career_id}/shortlist", response_model=CareerCandidatesResponse)
async def shortlist_career_candidate(
    student_id: str,
    career_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerCandidatesResponse:
    """Explicit student action, feeding Decision Memory — the reason is
    deterministically derived from the candidate's own Evidence Strength,
    never a fresh LLM call (see domain/services/decision_memory.py)."""
    profile = await profiles.get_or_create(student_id)
    candidate = next((c for c in profile.career_candidates if c.career_id == career_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Career candidate not found")

    now = datetime.now(timezone.utc)
    shortlist_candidate(profile, candidate, now)
    profile.updated_at = now
    await profiles.save(profile)

    return CareerCandidatesResponse(
        candidates=build_career_candidate_dtos(profile),
        insufficient_evidence=len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS,
        insufficient_evidence_reason=None,
    )


@router.post("/{student_id}/career-candidates/{career_id}/remove", response_model=CareerCandidatesResponse)
async def remove_career_candidate(
    student_id: str,
    career_id: str,
    profiles: StudentProfileRepository = Depends(get_student_profile_repository),
) -> CareerCandidatesResponse:
    """Explicit student-initiated discard — reuses the existing
    status/transition_reason fields (same ones automatic re-analysis
    already uses), with a reason built from the candidate's own
    missing_evidence, never a fresh LLM call."""
    profile = await profiles.get_or_create(student_id)
    candidate = next((c for c in profile.career_candidates if c.career_id == career_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Career candidate not found")

    now = datetime.now(timezone.utc)
    remove_candidate(profile, candidate, now)
    profile.updated_at = now
    await profiles.save(profile)

    return CareerCandidatesResponse(
        candidates=build_career_candidate_dtos(profile),
        insufficient_evidence=len(profile.career_dna.traits) < MIN_TRAITS_FOR_ANALYSIS,
        insufficient_evidence_reason=None,
    )
