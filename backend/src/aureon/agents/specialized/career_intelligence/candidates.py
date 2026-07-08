import uuid
from datetime import datetime

from aureon.agents.specialized.career_intelligence.confidence import compute_candidate_confidence
from aureon.agents.specialized.career_intelligence.schemas import CareerCandidateUpdate
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.student_profile import StudentProfile
from aureon.domain.services.evidence_recording import record_new_evidence

#: Evidence floor distinct from Discovery's 0.6 recommendation-confidence
#: gate (which governs Discovery's own internal mode) — Career
#: Intelligence is exploration-oriented and can reason at lower overall
#: confidence, but refuses to run at all with almost no signal.
MIN_TRAITS_FOR_ANALYSIS = 2


def _new_id() -> str:
    return str(uuid.uuid4())


def upsert_candidates(
    profile: StudentProfile,
    updates: list[CareerCandidateUpdate],
    careers_by_id: dict[str, str],
    now: datetime,
) -> None:
    """Turns this analysis's ``CareerCandidateUpdate`` list into persisted
    ``CareerCandidate``s + Evidence Graph entries + Notebook entries — the
    single place this happens, called by both the conversational agent and
    the direct analyze API route so the logic isn't duplicated."""
    by_id = {c.career_id: c for c in profile.career_candidates}
    updated_ids = {u.career_id for u in updates}

    for update in updates:
        career_name = careers_by_id.get(update.career_id, update.career_id)

        record_new_evidence(
            profile, related_career=update.career_id, items=update.supporting_evidence,
            relation="supports", now=now,
        )
        record_new_evidence(
            profile, related_career=update.career_id, items=update.contradicting_evidence,
            relation="contradicts", now=now,
        )

        confidence = compute_candidate_confidence(
            update.confidence,
            supporting_count=len(update.supporting_evidence),
            contradicting_count=len(update.contradicting_evidence),
        )

        existing = by_id.get(update.career_id)
        if existing is None:
            profile.career_candidates.append(
                CareerCandidate(
                    id=_new_id(),
                    career_id=update.career_id,
                    career_name=career_name,
                    why_it_matches=update.why_it_matches,
                    confidence=confidence,
                    uncertainty_reason=update.uncertainty_reason,
                    missing_evidence=update.missing_evidence,
                    updated_at=now,
                )
            )
            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=f"Aureon started considering {career_name} as a possible fit.",
                    source="conversation",
                    related_career=update.career_id,
                    previous_state="none",
                    new_evidence=update.supporting_evidence[0] if update.supporting_evidence else "",
                    updated_belief=f"Considering {career_name}",
                    reason=update.why_it_matches,
                    created_at=now,
                )
            )
            continue

        if existing.why_it_matches != update.why_it_matches or existing.confidence != confidence:
            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=f"Aureon's thinking on {career_name} was updated.",
                    source="conversation",
                    related_career=update.career_id,
                    previous_state=f"why: {existing.why_it_matches}",
                    new_evidence=update.supporting_evidence[0] if update.supporting_evidence else "",
                    updated_belief=update.why_it_matches,
                    reason=update.why_it_matches,
                    created_at=now,
                )
            )

        existing.why_it_matches = update.why_it_matches
        existing.confidence = confidence
        existing.uncertainty_reason = update.uncertainty_reason
        existing.missing_evidence = update.missing_evidence
        existing.status = "active"
        existing.transition_reason = None
        existing.updated_at = now

    for candidate in profile.career_candidates:
        if candidate.career_id not in updated_ids and candidate.status != "discarded":
            reason = "No longer surfaced by the most recent analysis."
            candidate.status = "discarded"
            candidate.transition_reason = reason
            candidate.updated_at = now
            profile.notebook_entries.append(
                NotebookEntry(
                    id=_new_id(),
                    kind="belief_revision",
                    text=f"Aureon set aside {candidate.career_name} as a candidate for now.",
                    source="conversation",
                    related_career=candidate.career_id,
                    previous_state="active",
                    new_evidence="",
                    updated_belief="discarded",
                    reason=reason,
                    created_at=now,
                )
            )
