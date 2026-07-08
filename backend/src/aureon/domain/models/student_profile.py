from datetime import datetime, timezone

from pydantic import BaseModel, Field

from aureon.domain.models.career_candidate import CareerCandidate
from aureon.domain.models.career_comparison import CareerComparison, ParallelUniverseScenario
from aureon.domain.models.career_dna import CareerDNA
from aureon.domain.models.career_experience import EventRegistration, ExpertSessionBooking, GuidanceRequest
from aureon.domain.models.career_exploration import CareerExplorationEvent
from aureon.domain.models.career_hypothesis import CareerHypothesis
from aureon.domain.models.career_investigation import CareerInvestigationRecord
from aureon.domain.models.career_simulation import CareerSimulation
from aureon.domain.models.document_investigation import DocumentInvestigationRecord
from aureon.domain.models.github_investigation import GitHubInvestigationRecord
from aureon.domain.models.decision_memory import DecisionMemoryEntry
from aureon.domain.models.evidence import EvidenceRecord
from aureon.domain.models.mentor_handoff import MentorHandoff
from aureon.domain.models.mentor_match import CollegeMatch, MentorMatch
from aureon.domain.models.notebook import NotebookEntry
from aureon.domain.models.reflection import ReflectionEntry


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ConfidenceSnapshot(BaseModel):
    """One point-in-time confidence reading, so the profile can show how
    certainty about the student grew (or didn't) over time rather than only
    exposing the latest number."""

    score: float
    source_agent: str
    recorded_at: datetime = Field(default_factory=_utcnow)


class ExplorationEvent(BaseModel):
    """A single piece of evidence gathered while in Exploration Mode, e.g. a
    reflection prompt answered or a micro-challenge completed. The `kind`
    field is a free-form label rather than an enum so new evidence sources
    (see agents/specialized/discovery/evidence/) can log events without a
    schema migration."""

    kind: str
    description: str
    occurred_at: datetime = Field(default_factory=_utcnow)


class CareerInteraction(BaseModel):
    career_name: str
    interaction_type: str  # e.g. "recommended", "compared", "shortlisted", "rejected"
    occurred_at: datetime = Field(default_factory=_utcnow)


class LearningProgress(BaseModel):
    roadmap_id: str | None = None
    milestones_completed: list[str] = Field(default_factory=list)
    last_updated_at: datetime = Field(default_factory=_utcnow)


class StudentProfile(BaseModel):
    """The long-term, cross-session model of a student.

    Unlike conversation state (which resets per session), this profile is
    loaded once per student at the start of every session and persisted
    after every turn via ``student_profile_repository``. It accumulates
    evidence rather than being overwritten, matching the product principle
    that recommendations get more accurate over time instead of being
    generated immediately from a single interaction.
    """

    student_id: str
    interests: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    persona: str | None = None

    confidence_score: float = 0.0
    confidence_history: list[ConfidenceSnapshot] = Field(default_factory=list)

    exploration_history: list[ExplorationEvent] = Field(default_factory=list)
    career_history: list[CareerInteraction] = Field(default_factory=list)
    learning_progress: LearningProgress = Field(default_factory=LearningProgress)
    mentor_interactions: list[MentorHandoff] = Field(default_factory=list)

    career_dna: CareerDNA = Field(default_factory=CareerDNA)
    career_hypotheses: list[CareerHypothesis] = Field(default_factory=list)
    reflection_journal: list[ReflectionEntry] = Field(default_factory=list)

    #: The Discovery Notebook's long-term memory — persisted here so it
    #: survives a refresh or a new device, instead of being reconstructed
    #: client-side from scratch each session.
    notebook_entries: list[NotebookEntry] = Field(default_factory=list)
    #: The single source of truth for evidence — trait/hypothesis
    #: evidence lists shown via the API are computed by filtering this,
    #: not stored redundantly elsewhere.
    evidence_graph: list[EvidenceRecord] = Field(default_factory=list)

    #: Phase 2 — careers the Career Intelligence Agent has reasoned about
    #: as possible fits, grounded in the same evidence graph above.
    career_candidates: list[CareerCandidate] = Field(default_factory=list)

    #: Observational exploration behavior (opened/bookmarked/revisited/
    #: etc.) — deliberately separate from evidence_graph/career_candidates.
    #: Never itself treated as evidence; Phase 3's Decision Agent is
    #: expected to interpret patterns across these events.
    career_exploration_history: list[CareerExplorationEvent] = Field(default_factory=list)

    #: Phase 3 — append-only history; each comparison/simulation run is
    #: its own real event, never overwritten.
    career_comparisons: list[CareerComparison] = Field(default_factory=list)
    parallel_universe_scenarios: list[ParallelUniverseScenario] = Field(default_factory=list)

    #: Phase 3 — same evolving-belief lifecycle as career_candidates.
    mentor_matches: list[MentorMatch] = Field(default_factory=list)
    college_matches: list[CollegeMatch] = Field(default_factory=list)

    #: Phase 3 — the short, explained log of decision-relevant actions.
    decision_memory: list[DecisionMemoryEntry] = Field(default_factory=list)

    #: V10 — Multi-Source Search Intelligence; append-only, same
    #: never-overwritten reasoning as career_comparisons. Also doubles as
    #: this capability's own "previous investigations" memory.
    career_investigations: list[CareerInvestigationRecord] = Field(default_factory=list)

    #: V11 — Career Simulator & Decision Laboratory; append-only, same
    #: never-overwritten reasoning as career_comparisons.
    career_simulations: list[CareerSimulation] = Field(default_factory=list)

    #: V12 — Investigation History; append-only. Backfills the persisted
    #: shape GitHub/Document Intelligence never had (V9/V8 only left
    #: Evidence/Notebook trails) so both become genuinely reopenable.
    github_investigations: list[GitHubInvestigationRecord] = Field(default_factory=list)
    document_investigations: list[DocumentInvestigationRecord] = Field(default_factory=list)

    #: V13 — Career Exploration Ecosystem (Expert Connect). Append-only/
    #: toggle, same never-overwritten reasoning as career_comparisons.
    expert_session_bookings: list[ExpertSessionBooking] = Field(default_factory=list)
    guidance_requests: list[GuidanceRequest] = Field(default_factory=list)
    event_registrations: list[EventRegistration] = Field(default_factory=list)
    #: Bookmark list — mentor ids only, per the spec's explicit "no
    #: complex backend logic" for Save Expert.
    saved_experts: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
