import uuid
from datetime import datetime
from typing import Literal

from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.student_profile import StudentProfile

"""Shared Evidence Graph writer, used by the Discovery Agent (hypothesis
evidence), the Career Intelligence Agent (candidate evidence), and the
Decision Agent (mentor/institution match evidence) — one dedup/append
implementation instead of structurally identical copies differing only
in which cross-reference field they set."""


def record_new_evidence(
    profile: StudentProfile,
    *,
    items: list[str],
    relation: Literal["supports", "contradicts"],
    now: datetime,
    source: Literal["conversation", "reflection", "url", "document", "github", "search", "experiment"] = "conversation",
    related_trait: str | None = None,
    related_hypothesis: str | None = None,
    related_career: str | None = None,
    related_mentor: str | None = None,
    related_institution: str | None = None,
) -> None:
    """Only newly-seen evidence strings become new EvidenceRecords — the
    LLM tends to re-state the full current supporting/contradicting list
    each turn/analysis, not just deltas, so this dedupes against what's
    already in the graph for this exact hypothesis/career/mentor/
    institution/trait.

    ``source``/``related_trait`` are additive, backward-compatible
    parameters (Discover Batch 2) — every pre-existing caller omits both
    and keeps writing ``source="conversation"`` records exactly as before.
    """
    existing_texts = {
        e.text
        for e in profile.evidence_graph
        if e.related_hypothesis == related_hypothesis
        and e.related_career == related_career
        and e.related_mentor == related_mentor
        and e.related_institution == related_institution
        and e.related_trait == related_trait
        and e.relation == relation
    }
    for text in items:
        if text in existing_texts:
            continue
        profile.evidence_graph.append(
            EvidenceRecord(
                id=str(uuid.uuid4()),
                text=text,
                source=source,
                related_trait=related_trait,
                related_hypothesis=related_hypothesis,
                related_career=related_career,
                related_mentor=related_mentor,
                related_institution=related_institution,
                relation=relation,
                created_at=now,
            )
        )
