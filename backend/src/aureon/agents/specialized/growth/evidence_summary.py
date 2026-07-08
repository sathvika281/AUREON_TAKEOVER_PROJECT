from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from aureon.domain.models.progress_report import ProgressDirection, ProgressTimelineWindow
from aureon.domain.models.student_profile import StudentProfile

#: The two adjacent cadence buckets every count-based dimension compares:
#: "recent" (last 7 days) vs. "previous" (the 23 days before that). A
#: dimension whose recent bucket is busier than its previous one is
#: "improving" — never an LLM-asserted judgment, always this same real
#: delta.
RECENT_WINDOW_DAYS = 7
MID_WINDOW_DAYS = 30

#: Below this combined real-evidence count, Progress Intelligence refuses
#: to reason at all rather than stretch thin evidence into a report.
MIN_EVIDENCE_FOR_PROGRESS_REPORT = 5


@dataclass
class DimensionEvidence:
    key: str
    label: str
    direction: ProgressDirection
    evidence_summary: list[str] = field(default_factory=list)


@dataclass
class ProgressEvidenceBundle:
    dimensions: list[DimensionEvidence]
    timeline: list[ProgressTimelineWindow]
    total_evidence_count: int
    insufficient_evidence: bool
    insufficient_evidence_reason: str | None = None


def _bucket_counts(timestamps: list[datetime], now: datetime) -> tuple[int, int, int]:
    """(recent 7-day count, previous 23-day count, all-time count)."""
    recent_cutoff = now - timedelta(days=RECENT_WINDOW_DAYS)
    mid_cutoff = now - timedelta(days=MID_WINDOW_DAYS)
    recent = sum(1 for ts in timestamps if ts >= recent_cutoff)
    previous = sum(1 for ts in timestamps if mid_cutoff <= ts < recent_cutoff)
    return recent, previous, len(timestamps)


def _direction_from_counts(recent: int, previous: int) -> ProgressDirection:
    if recent == 0 and previous == 0:
        return "not_enough_evidence"
    if recent > previous:
        return "improving"
    if recent < previous:
        return "slowing"
    return "steady"


def _cadence_dimension(
    key: str, label: str, timestamps: list[datetime], now: datetime, unit: str
) -> DimensionEvidence:
    recent, previous, total = _bucket_counts(timestamps, now)
    direction = _direction_from_counts(recent, previous)
    summary = [
        f"{recent} {unit} in the last {RECENT_WINDOW_DAYS} days "
        f"(was {previous} in the previous {MID_WINDOW_DAYS - RECENT_WINDOW_DAYS} days)",
        f"{total} {unit} total since the student started",
    ]
    return DimensionEvidence(key=key, label=label, direction=direction, evidence_summary=summary)


def _career_clarity_dimension(profile: StudentProfile, now: datetime) -> DimensionEvidence:
    """Clarity is about direction, not activity volume — grounded in the
    confidence_score trend and hypothesis/candidate lifecycle state
    rather than a raw event count."""
    history = sorted(profile.confidence_history, key=lambda s: s.recorded_at)
    summary: list[str] = []
    direction: ProgressDirection = "not_enough_evidence"

    if history:
        mid_cutoff = now - timedelta(days=MID_WINDOW_DAYS)
        past_snapshot = next((s for s in history if s.recorded_at >= mid_cutoff), history[0])
        current = profile.confidence_score
        past = past_snapshot.score
        if current > past:
            direction = "improving"
        elif current < past:
            direction = "slowing"
        else:
            direction = "steady"
        summary.append(f"Confidence score moved from {past:.2f} to {current:.2f} over the tracked period")

    shortlisted = [c for c in profile.career_candidates if c.is_shortlisted and c.status != "discarded"]
    if shortlisted:
        summary.append(f"Currently shortlisted: {shortlisted[0].career_name}")

    strong_or_validated = [h for h in profile.career_hypotheses if h.status in ("strong", "validated")]
    if strong_or_validated:
        summary.append(
            f"{len(strong_or_validated)} hypothesis(es) reached strong/validated status: "
            + ", ".join(h.career_name for h in strong_or_validated)
        )

    if not summary:
        summary.append("No hypothesis or candidate history recorded yet.")

    return DimensionEvidence(key="career_clarity", label="Career Clarity", direction=direction, evidence_summary=summary)


def _timeline_windows(profile: StudentProfile, now: datetime) -> list[ProgressTimelineWindow]:
    """Pure read-aggregation, no LLM — same philosophy as
    domain/services/decision_timeline.py."""
    recent_cutoff = now - timedelta(days=RECENT_WINDOW_DAYS)
    mid_cutoff = now - timedelta(days=MID_WINDOW_DAYS)

    all_timestamps: list[datetime] = (
        [e.created_at for e in profile.notebook_entries]
        + [r.answered_at for r in profile.reflection_journal if r.answered_at]
        + [e.created_at for e in profile.career_exploration_history]
        + [c.created_at for c in profile.career_comparisons]
        + [s.created_at for s in profile.parallel_universe_scenarios]
        + [d.created_at for d in profile.decision_memory]
    )

    last_week = [ts for ts in all_timestamps if ts >= recent_cutoff]
    last_month = [ts for ts in all_timestamps if mid_cutoff <= ts < recent_cutoff]
    overall = all_timestamps

    return [
        ProgressTimelineWindow(
            label="Last Week",
            description=f"{len(last_week)} recorded events" if last_week else "No recorded activity",
            event_count=len(last_week),
        ),
        ProgressTimelineWindow(
            label="Last Month",
            description=f"{len(last_month)} recorded events" if last_month else "No recorded activity",
            event_count=len(last_month),
        ),
        ProgressTimelineWindow(
            label="Overall Journey",
            description=f"{len(overall)} recorded events since the student started",
            event_count=len(overall),
        ),
    ]


def assemble_progress_evidence(
    profile: StudentProfile, *, now: datetime | None = None
) -> ProgressEvidenceBundle:
    """Deterministic evidence assembly for Progress Intelligence — no LLM
    call happens here. Every dimension's direction is computed from real
    timestamps/deltas already stored on StudentProfile; the LLM (see
    reasoning.py) only ever explains *why*, on top of these facts."""
    now = now or datetime.now(timezone.utc)

    dimensions = [
        _cadence_dimension(
            "exploration", "Exploration",
            [e.created_at for e in profile.career_exploration_history], now, "career exploration events",
        ),
        _career_clarity_dimension(profile, now),
        _cadence_dimension(
            "decision_confidence", "Decision Confidence",
            [c.created_at for c in profile.career_comparisons]
            + [s.created_at for s in profile.parallel_universe_scenarios]
            + [d.created_at for d in profile.decision_memory],
            now, "decision-support actions",
        ),
        _cadence_dimension(
            "reflection_consistency", "Reflection Consistency",
            [r.answered_at for r in profile.reflection_journal if r.answered_at], now, "answered reflections",
        ),
        _cadence_dimension(
            "skill_development", "Skill Development",
            [e.created_at for e in profile.notebook_entries if e.kind == "observation"],
            now, "new Career DNA observations",
        ),
    ]

    total_evidence_count = (
        len(profile.notebook_entries)
        + len(profile.reflection_journal)
        + len(profile.career_exploration_history)
        + len(profile.career_comparisons)
        + len(profile.parallel_universe_scenarios)
        + len(profile.decision_memory)
        + len(profile.confidence_history)
    )
    insufficient = total_evidence_count < MIN_EVIDENCE_FOR_PROGRESS_REPORT

    return ProgressEvidenceBundle(
        dimensions=dimensions,
        timeline=_timeline_windows(profile, now),
        total_evidence_count=total_evidence_count,
        insufficient_evidence=insufficient,
        insufficient_evidence_reason=(
            f"Only {total_evidence_count} pieces of evidence recorded so far (notebook entries, "
            "reflections, exploration events, comparisons, and decisions combined) — Progress "
            "Intelligence needs a broader trail before it can reason about trends responsibly. "
            "Keep exploring in Identity Discovery, reflecting, and comparing careers; this becomes "
            "more accurate as that evidence accumulates."
            if insufficient
            else None
        ),
    )
