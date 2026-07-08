import uuid
from datetime import datetime

from aureon.agents.specialized.decision.confidence import evidence_strength_label
from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_comparison import CareerComparison
from aureon.domain.models.decision_memory import DecisionMemoryEntry
from aureon.domain.models.student_profile import StudentProfile

"""Decision Memory writers — the short, explained log of decision-relevant
actions. Every reason here is derived from data already computed
elsewhere (a comparison's own summary, or a candidate's evidence_strength/
missing_evidence), never a fresh, separate LLM call."""


def _new_id() -> str:
    return str(uuid.uuid4())


def record_comparison_memory(
    profile: StudentProfile, comparison: CareerComparison, now: datetime
) -> DecisionMemoryEntry:
    entry = DecisionMemoryEntry(
        id=_new_id(),
        action_type="compared",
        career_ids=comparison.career_ids,
        career_names=comparison.career_names,
        reason=comparison.summary_reason,
        created_at=now,
    )
    profile.decision_memory.append(entry)
    return entry


def shortlist_candidate(
    profile: StudentProfile, candidate: CareerCandidate, now: datetime
) -> DecisionMemoryEntry:
    candidate.is_shortlisted = True
    candidate.updated_at = now
    reason = f"{evidence_strength_label(candidate.confidence)} alignment with current evidence."
    entry = DecisionMemoryEntry(
        id=_new_id(),
        action_type="shortlisted",
        career_ids=[candidate.career_id],
        career_names={candidate.career_id: candidate.career_name},
        reason=reason,
        created_at=now,
    )
    profile.decision_memory.append(entry)
    return entry


def remove_candidate(
    profile: StudentProfile, candidate: CareerCandidate, now: datetime
) -> DecisionMemoryEntry:
    gap = candidate.missing_evidence[0] if candidate.missing_evidence else "a clearer overall fit"
    reason = f"Not enough evidence for {gap}."
    candidate.status = "discarded"
    candidate.transition_reason = reason
    candidate.updated_at = now
    entry = DecisionMemoryEntry(
        id=_new_id(),
        action_type="removed",
        career_ids=[candidate.career_id],
        career_names={candidate.career_id: candidate.career_name},
        reason=reason,
        created_at=now,
    )
    profile.decision_memory.append(entry)
    return entry
