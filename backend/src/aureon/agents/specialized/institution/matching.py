import uuid
from datetime import datetime

from aureon.agents.specialized.institution.confidence import compute_candidate_confidence
from aureon.agents.specialized.institution.prompts import build_college_match_messages
from aureon.agents.specialized.institution.schemas import (
    COLLEGE_MATCH_TOOL,
    CollegeMatchTurnOutput,
    CollegeMatchUpdate,
)
from aureon.domain.models.institution import Institution
from aureon.domain.models.mentor_match import CollegeMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence
from aureon.services.llm.base import LLMClient


def _new_id() -> str:
    return str(uuid.uuid4())


async def analyze_college_matches(
    profile: StudentProfile, institutions: list[Institution], *, llm: LLMClient
) -> CollegeMatchTurnOutput:
    """Institution Agent's own reasoning entry point — relocated from the
    Decision Agent's module, which never should have owned this. Called
    both by the direct API route (api/v1/decision.py) and, when needed,
    via delegation from Decision through the Mission Orchestrator."""
    messages = build_college_match_messages(
        career_dna=profile.career_dna,
        evidence_graph=profile.evidence_graph,
        career_candidates=profile.career_candidates,
        institutions=institutions,
    )
    response = await llm.complete(messages, tools=[COLLEGE_MATCH_TOOL], tool_choice="required")
    if not response.tool_calls:
        return CollegeMatchTurnOutput(
            reply_to_student=response.content or "Let's gather more evidence before matching institutions.",
            insufficient_evidence=True,
            insufficient_evidence_reason="Analysis could not be completed this time.",
        )
    return CollegeMatchTurnOutput.model_validate(response.tool_calls[0].arguments)


def upsert_college_matches(
    profile: StudentProfile,
    updates: list[CollegeMatchUpdate],
    institutions_by_id: dict[str, str],
    now: datetime,
) -> None:
    """Mirrors mentor/matching.py::upsert_mentor_matches exactly, for
    institutions."""
    by_id = {c.institution_id: c for c in profile.college_matches}
    updated_ids = {u.institution_id for u in updates}

    for update in updates:
        institution_name = institutions_by_id.get(update.institution_id, update.institution_id)
        record_new_evidence(
            profile, related_institution=update.institution_id, items=update.supporting_evidence,
            relation="supports", now=now,
        )
        record_new_evidence(
            profile, related_institution=update.institution_id, items=update.contradicting_evidence,
            relation="contradicts", now=now,
        )
        confidence = compute_candidate_confidence(
            update.confidence,
            supporting_count=len(update.supporting_evidence),
            contradicting_count=len(update.contradicting_evidence),
        )
        existing = by_id.get(update.institution_id)
        if existing is None:
            profile.college_matches.append(
                CollegeMatch(
                    id=_new_id(), institution_id=update.institution_id, institution_name=institution_name,
                    why_it_matches=update.why_it_matches, confidence=confidence,
                    uncertainty_reason=update.uncertainty_reason,
                    missing_evidence=update.missing_evidence, updated_at=now,
                )
            )
            continue
        existing.why_it_matches = update.why_it_matches
        existing.confidence = confidence
        existing.uncertainty_reason = update.uncertainty_reason
        existing.missing_evidence = update.missing_evidence
        existing.status = "active"
        existing.transition_reason = None
        existing.updated_at = now

    for match in profile.college_matches:
        if match.institution_id not in updated_ids and match.status != "discarded":
            match.status = "discarded"
            match.transition_reason = "No longer surfaced by the most recent analysis."
            match.updated_at = now
