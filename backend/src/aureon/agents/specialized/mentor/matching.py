import uuid
from datetime import datetime

from aureon.agents.specialized.mentor.confidence import compute_candidate_confidence
from aureon.agents.specialized.mentor.prompts import build_mentor_match_messages
from aureon.agents.specialized.mentor.schemas import MENTOR_MATCH_TOOL, MentorMatchTurnOutput, MentorMatchUpdate
from aureon.domain.models.mentor import Mentor
from aureon.domain.models.mentor_match import MentorMatch
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence
from aureon.services.llm.base import LLMClient


def _new_id() -> str:
    return str(uuid.uuid4())


async def analyze_mentor_matches(
    profile: StudentProfile, mentors: list[Mentor], *, llm: LLMClient
) -> MentorMatchTurnOutput:
    """Mentor Agent's own reasoning entry point — relocated from the
    Decision Agent's module, which never should have owned this. Called
    both by the direct API route (api/v1/decision.py) and, when needed,
    via delegation from Decision through the Mission Orchestrator."""
    messages = build_mentor_match_messages(
        career_dna=profile.career_dna,
        evidence_graph=profile.evidence_graph,
        career_candidates=profile.career_candidates,
        mentors=mentors,
    )
    response = await llm.complete(messages, tools=[MENTOR_MATCH_TOOL], tool_choice="required")
    if not response.tool_calls:
        return MentorMatchTurnOutput(
            reply_to_student=response.content or "Let's gather more evidence before matching mentors.",
            insufficient_evidence=True,
            insufficient_evidence_reason="Analysis could not be completed this time.",
        )
    return MentorMatchTurnOutput.model_validate(response.tool_calls[0].arguments)


def upsert_mentor_matches(
    profile: StudentProfile,
    updates: list[MentorMatchUpdate],
    mentors_by_id: dict[str, str],
    now: datetime,
) -> None:
    """Same active/discarded lifecycle as Career Candidates
    (career_intelligence/candidates.py::upsert_candidates) — a mentor
    match absent from a later analysis is kept, marked discarded, not
    deleted. Runs even when `updates` is empty, so a genuinely-empty
    result still discards previously-active matches rather than leaving
    them stale."""
    by_id = {m.mentor_id: m for m in profile.mentor_matches}
    updated_ids = {u.mentor_id for u in updates}

    for update in updates:
        mentor_name = mentors_by_id.get(update.mentor_id, update.mentor_id)
        record_new_evidence(
            profile, related_mentor=update.mentor_id, items=update.supporting_evidence,
            relation="supports", now=now,
        )
        record_new_evidence(
            profile, related_mentor=update.mentor_id, items=update.contradicting_evidence,
            relation="contradicts", now=now,
        )
        confidence = compute_candidate_confidence(
            update.confidence,
            supporting_count=len(update.supporting_evidence),
            contradicting_count=len(update.contradicting_evidence),
        )
        existing = by_id.get(update.mentor_id)
        if existing is None:
            profile.mentor_matches.append(
                MentorMatch(
                    id=_new_id(), mentor_id=update.mentor_id, mentor_name=mentor_name,
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

    for match in profile.mentor_matches:
        if match.mentor_id not in updated_ids and match.status != "discarded":
            match.status = "discarded"
            match.transition_reason = "No longer surfaced by the most recent analysis."
            match.updated_at = now
