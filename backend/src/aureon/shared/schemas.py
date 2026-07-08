from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ConversationTurnRequest(BaseModel):
    """Request DTO for POST /v1/conversation/turn."""

    student_id: str
    conversation_id: str | None = None  # None starts a new conversation
    message: str


class TraitSignalDTO(BaseModel):
    score: float | None
    summary: str


class CareerHypothesisDTO(BaseModel):
    career_name: str
    confidence: float
    status: str
    transition_reason: str | None
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    missing_evidence: list[str]


class SuggestedActivityDTO(BaseModel):
    title: str
    description: str
    reason: str


class ReflectionEntryDTO(BaseModel):
    prompt: str
    response: str | None
    created_at: datetime
    answered_at: datetime | None


class NotebookEntryDTO(BaseModel):
    id: str
    kind: str
    text: str
    source: str
    related_trait: str | None
    related_hypothesis: str | None
    related_career: str | None
    confidence_label: str | None
    previous_state: str | None
    new_evidence: str | None
    updated_belief: str | None
    reason: str | None
    created_at: datetime


class EvidenceRecordDTO(BaseModel):
    id: str
    text: str
    source: str
    related_trait: str | None
    related_hypothesis: str | None
    related_career: str | None
    relation: str
    created_at: datetime


class HiddenPotentialPatternDTO(BaseModel):
    id: str
    trait_a: str
    trait_b: str
    sentence: str
    supporting_evidence: list[str]


class ConversationTurnResponse(BaseModel):
    """Response DTO for POST /v1/conversation/turn. Bundles the Career
    Evidence Engine's transparency data (career_dna, hypotheses) alongside
    the reply so the frontend can render the Discovery Notebook without an
    extra round trip on every turn."""

    conversation_id: str
    reply: str
    mode: str
    active_agent: str | None
    confidence_score: float
    understanding_stage: str
    understanding_narrative: str
    career_dna: dict[str, TraitSignalDTO]
    hypotheses: list[CareerHypothesisDTO]
    hidden_potential: list[HiddenPotentialPatternDTO]
    notebook_entries: list[NotebookEntryDTO]
    reflection_prompt: str | None
    suggested_activity: SuggestedActivityDTO | None


class DiscoveryProfileResponse(BaseModel):
    """Response DTO for GET /v1/students/{student_id}/discovery-profile —
    lets the frontend restore the Discovery Notebook for a returning
    student without replaying the whole conversation."""

    student_id: str
    confidence_score: float
    understanding_stage: str
    understanding_narrative: str
    career_dna: dict[str, TraitSignalDTO]
    hypotheses: list[CareerHypothesisDTO]
    hidden_potential: list[HiddenPotentialPatternDTO]
    notebook_entries: list[NotebookEntryDTO]
    evidence_graph: list[EvidenceRecordDTO]
    reflection_journal: list[ReflectionEntryDTO]


class SalaryRangeDTO(BaseModel):
    region: str
    range: str
    note: str


class CareerRealityDTO(BaseModel):
    daily_work: str
    work_environment: str
    collaboration_level: str
    creativity_level: str
    research_intensity: str
    learning_curve: str
    travel: str
    remote_possibility: str
    stress_factors: str
    typical_challenges: str
    misconceptions: str
    long_term_growth: str
    salary_ranges: list[SalaryRangeDTO]
    required_education: str
    required_skills: list[str]
    entrepreneurship_potential: str


class FutureLensDTO(BaseModel):
    ai_impact: str
    automation_risk: str
    demand_2030: str
    demand_2035: str
    demand_2040: str
    emerging_opportunities: str
    skills_becoming_valuable: list[str]
    timeline_narrative: str


class CareerSummaryDTO(BaseModel):
    id: str
    name: str
    category: str
    industry: str
    countries: list[str]
    one_liner: str
    trait_tags: list[str]


class CareerStoryDTO(BaseModel):
    id: str
    career_id: str
    person_label: str
    background: str
    journey: str
    challenges: str
    turning_points: str
    advice: str
    lessons_learned: str
    relevant_to_student: bool


class CareerDetailDTO(BaseModel):
    id: str
    name: str
    category: str
    industry: str
    countries: list[str]
    one_liner: str
    trait_tags: list[str]
    reality: CareerRealityDTO
    future_lens: FutureLensDTO
    stories: list[CareerStoryDTO]


class CareerCandidateDTO(BaseModel):
    career_id: str
    career_name: str
    why_it_matches: str
    evidence_strength: str
    uncertainty_reason: str | None
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    missing_evidence: list[str]
    is_shortlisted: bool = False


class CareerCandidatesResponse(BaseModel):
    candidates: list[CareerCandidateDTO]
    insufficient_evidence: bool
    insufficient_evidence_reason: str | None
    #: V13 — real, deterministic pulls from the student's own already-
    #: triggered Mentor Match/Institution Match analysis; never a fresh
    #: LLM call, never fabricated. Empty until the student has run those.
    recommended_colleges: list[str] = []
    recommended_experts: list[str] = []


class CareerExplorationEventDTO(BaseModel):
    id: str
    career_id: str
    interaction_type: str
    metadata: dict[str, Any]
    created_at: datetime


class RecordCareerExplorationEventRequest(BaseModel):
    career_id: str
    interaction_type: str
    metadata: dict[str, Any] = {}


class RecordCareerExplorationEventResponse(BaseModel):
    recorded: bool


class CareerExplorationHistoryResponse(BaseModel):
    events: list[CareerExplorationEventDTO]


class MentorSummaryDTO(BaseModel):
    id: str
    name: str
    role_type: str
    field: str
    bio: str
    trait_tags: list[str]
    learning_style_fit: str
    #: V13 — Expert Connect additive fields.
    organization: str
    years_experience: int
    journey_highlights: list[str]
    discussion_topics: list[str]


class CareerEventDTO(BaseModel):
    id: str
    title: str
    event_type: str
    institution_id: str | None
    mentor_id: str | None
    description: str
    scheduled_at: datetime


class MentorDetailDTO(MentorSummaryDTO):
    """V13 — the mentor-detail route that never existed before (only the
    institution equivalent did). Adds real, deterministically-generated
    slots and any real seeded career talks this expert hosts — never a
    fabricated schedule."""

    available_slots: list[datetime]
    upcoming_career_talks: list[CareerEventDTO]


class ResearchLabDTO(BaseModel):
    id: str
    name: str
    focus_area: str
    description: str


class StudentOrganizationDTO(BaseModel):
    id: str
    name: str
    focus_area: str
    description: str


class AcademicProgramDTO(BaseModel):
    id: str
    name: str
    degree_type: str
    field: str
    description: str


class InnovationCenterDTO(BaseModel):
    id: str
    name: str
    focus_area: str
    description: str


class FacultyHighlightDTO(BaseModel):
    id: str
    name: str
    title: str
    expertise_area: str
    bio: str


class StudentAmbassadorDTO(BaseModel):
    id: str
    student_label: str
    program: str
    message: str


class StudentProjectDTO(BaseModel):
    id: str
    student_label: str
    project_title: str
    description: str
    skills_used: list[str]


class InternshipOpportunityDTO(BaseModel):
    id: str
    title: str
    field: str
    description: str


class InstitutionSummaryDTO(BaseModel):
    id: str
    name: str
    country: str
    city: str
    trait_tags: list[str]
    is_partner: bool


class InstitutionDetailDTO(BaseModel):
    id: str
    name: str
    country: str
    city: str
    research_culture: str
    innovation_ecosystem: str
    industry_collaboration: str
    placements: str
    learning_environment: str
    trait_tags: list[str]
    is_partner: bool
    research_labs: list[ResearchLabDTO]
    student_organizations: list[StudentOrganizationDTO]
    academic_programs: list[AcademicProgramDTO]
    #: V13 — College Collaboration additive sections (empty lists for
    #: every non-partner institution, real seeded data for NIAT).
    innovation_centers: list[InnovationCenterDTO]
    faculty_highlights: list[FacultyHighlightDTO]
    student_ambassadors: list[StudentAmbassadorDTO]
    student_projects: list[StudentProjectDTO]
    internship_opportunities: list[InternshipOpportunityDTO]
    upcoming_events: list[CareerEventDTO]


class AgentStatusDTO(BaseModel):
    name: str
    display_name: str
    status: str


class DelegationDTO(BaseModel):
    from_agent: str
    to_agent: str
    capability: str
    reason: str


class MissionEvidenceDTO(BaseModel):
    source: str
    summary: str
    reliability: str | None
    source_type: str | None
    title: str | None
    confidence: float | None
    metadata: dict[str, Any]
    timestamp: datetime


class ToolExecutionDTO(BaseModel):
    tool_name: str
    status: str
    explanation: str | None
    evidence: list[MissionEvidenceDTO]


class MissionSnapshotDTO(BaseModel):
    """V7 — Mission Workspace. A pure read-out of a Mission's already-real
    execution data; every mission-backed route attaches one of these,
    unmodified in shape, regardless of which feature produced it."""

    stages: list[str]
    agents: list[AgentStatusDTO]
    delegations: list[DelegationDTO]
    tools: list[ToolExecutionDTO]
    evidence: list[MissionEvidenceDTO]
    narration: list[str]


class MentorMatchDTO(BaseModel):
    mentor_id: str
    mentor_name: str
    why_it_matches: str
    evidence_strength: str
    uncertainty_reason: str | None
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    missing_evidence: list[str]


class MentorMatchesResponse(BaseModel):
    matches: list[MentorMatchDTO]
    insufficient_evidence: bool
    insufficient_evidence_reason: str | None
    mission: MissionSnapshotDTO | None = None
    artifacts_updated: list[str] = []


class CollegeMatchDTO(BaseModel):
    institution_id: str
    institution_name: str
    why_it_matches: str
    evidence_strength: str
    uncertainty_reason: str | None
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    missing_evidence: list[str]


class CollegeMatchesResponse(BaseModel):
    matches: list[CollegeMatchDTO]
    insufficient_evidence: bool
    insufficient_evidence_reason: str | None
    mission: MissionSnapshotDTO | None = None
    artifacts_updated: list[str] = []


class ComparisonDimensionDTO(BaseModel):
    dimension: str
    per_career: dict[str, str]
    why_it_matters_to_you: str


class CareerComparisonDTO(BaseModel):
    id: str
    career_ids: list[str]
    career_names: dict[str, str]
    dimensions: list[ComparisonDimensionDTO]
    summary_reason: str
    missing_evidence: list[str]
    created_at: datetime


class CareerComparisonRequest(BaseModel):
    career_ids: list[str]


class CareerComparisonsResponse(BaseModel):
    comparisons: list[CareerComparisonDTO]
    #: V13 — same real, deterministic pulls as CareerCandidatesResponse.
    recommended_colleges: list[str] = []
    recommended_experts: list[str] = []


class ParallelUniverseBranchDTO(BaseModel):
    career_id: str
    career_name: str
    daily_work: str
    lifestyle: str
    growth: str
    challenges: str
    future_opportunities: str


class ParallelUniverseScenarioDTO(BaseModel):
    id: str
    branches: list[ParallelUniverseBranchDTO]
    framing_note: str
    missing_evidence: list[str]
    created_at: datetime


class ParallelUniverseRequest(BaseModel):
    career_ids: list[str]


class ParallelUniverseResponse(BaseModel):
    scenarios: list[ParallelUniverseScenarioDTO]


class SimulatedJourneyPhaseDTO(BaseModel):
    phase: str
    focus: str
    milestones: list[str]


class TradeOffAnalysisDTO(BaseModel):
    advantages: list[str]
    challenges: list[str]
    opportunities: list[str]
    sacrifices: list[str]
    uncertainties: list[str]


class CareerPathSimulationDTO(BaseModel):
    career_id: str
    career_name: str
    required_skills: str
    higher_education_path: str
    work_environment: str
    lifestyle: str
    typical_challenges: str
    growth_potential: str
    risk_factors: str
    research_opportunities: str
    industry_opportunities: str
    future_adaptability: str
    career_dna_alignment: str
    student_interest_alignment: str
    evidence_confidence: str
    learning_journey: str
    expected_milestones: list[str]
    timeline: list[SimulatedJourneyPhaseDTO]
    trade_offs: TradeOffAnalysisDTO
    next_best_actions: list[str]


class DecisionInsightsDTO(BaseModel):
    strongest_match_career_id: str | None
    why: str
    possible_risks: list[str]
    questions_to_explore: list[str]
    recommended_next_investigation: str
    recommended_mentors: list[str]
    recommended_institutions: list[str]
    recommended_resources: list[str]


class CareerSimulationDTO(BaseModel):
    id: str
    career_ids: list[str]
    career_names: dict[str, str]
    simulations: list[CareerPathSimulationDTO]
    decision_insights: DecisionInsightsDTO
    missing_evidence: list[str]
    created_at: datetime


class CareerSimulationRequest(BaseModel):
    career_ids: list[str]


class CareerSimulationsResponse(BaseModel):
    simulations: list[CareerSimulationDTO]
    insufficient_evidence: bool = False
    insufficient_evidence_reason: str | None = None
    mission: MissionSnapshotDTO | None = None
    artifacts_updated: list[str] = []


class DecisionTimelineMilestoneDTO(BaseModel):
    kind: str
    text: str
    created_at: datetime


class DecisionTimelineResponse(BaseModel):
    milestones: list[DecisionTimelineMilestoneDTO]
    current_direction_summary: str


class DecisionMemoryEntryDTO(BaseModel):
    id: str
    action_type: str
    career_ids: list[str]
    career_names: dict[str, str]
    reason: str
    created_at: datetime


class DecisionMemoryResponse(BaseModel):
    entries: list[DecisionMemoryEntryDTO]


class ProgressDimensionDTO(BaseModel):
    key: str
    label: str
    direction: str
    evidence_summary: list[str]
    reasoning: str


class ProgressTimelineWindowDTO(BaseModel):
    label: str
    description: str
    event_count: int


class ProgressPriorityDTO(BaseModel):
    rank: int
    action: str
    evidence: str


class ProgressReportResponse(BaseModel):
    overall_narrative: str
    dimensions: list[ProgressDimensionDTO]
    growing_strengths: list[str]
    areas_slowing_down: list[str]
    recent_improvements: list[str]
    timeline: list[ProgressTimelineWindowDTO]
    next_priorities: list[ProgressPriorityDTO]
    insufficient_evidence: bool
    insufficient_evidence_reason: str | None
    generated_at: datetime
    mission: MissionSnapshotDTO | None = None
    artifacts_updated: list[str] = []


class UrlInvestigationRequest(BaseModel):
    url: str


class UrlInvestigationResponse(BaseModel):
    url: str
    category: str
    owning_specialist: str
    delegated: bool
    status: str
    title: str | None
    summary: str | None
    key_findings: list[str]
    structured_fields: dict[str, str]
    explanation: str | None
    stages: list[str]
    evidence_added: bool
    mission: MissionSnapshotDTO
    artifacts_updated: list[str]


class DocumentInvestigationResponse(BaseModel):
    filename: str
    category: str
    owning_specialist: str
    matched_on: str
    status: str
    title: str | None
    summary: str | None
    key_findings: list[str]
    structured_fields: dict[str, str]
    explanation: str | None
    stages: list[str]
    evidence_added: bool
    mission: MissionSnapshotDTO
    artifacts_updated: list[str]


class GitHubInvestigationRequest(BaseModel):
    url: str


class GitHubSkillDTO(BaseModel):
    skill: str
    category: str
    evidence: str


class GitHubRepoSummaryDTO(BaseModel):
    """Metadata for display only — stars/forks/last_activity are shown
    honestly to the student but never fed into any reasoning step or
    Career DNA update (see github_evidence.py's DisplayMetadata)."""

    name: str
    description: str
    owner: str
    primary_language: str | None
    languages: list[str]
    topics: list[str]
    license: str | None
    stars: int
    forks: int
    last_activity: str | None


class GitHubInvestigationResponse(BaseModel):
    url: str
    status: str
    explanation: str | None
    repo: GitHubRepoSummaryDTO | None
    skills: list[GitHubSkillDTO]
    overall_summary: str | None
    project_purpose: str | None
    technical_complexity: str | None
    problem_solving: str | None
    code_organization: str | None
    technology_breadth: str | None
    documentation_quality: str | None
    learning_signals: str | None
    engineering_maturity: str | None
    research_orientation: str | None
    ai_ml_signals: str | None
    stages: list[str]
    evidence_added: bool
    mission: MissionSnapshotDTO
    artifacts_updated: list[str]


class SearchInvestigationRequest(BaseModel):
    question: str


class FindingDTO(BaseModel):
    claim: str
    status: str
    citing_sources: list[str]
    explanation: str


class SourceStatusDTO(BaseModel):
    """Display-only — see search_sources.py::SourceAvailability. Never
    reflects or influences the findings/overall_summary below it."""

    name: str
    category: str
    reached: bool
    note: str | None


class SourceAvailabilityDTO(BaseModel):
    total_sources: int
    sources_retrieved: int
    sources_unavailable: int
    sources: list[SourceStatusDTO]


class SearchInvestigationResponse(BaseModel):
    question: str
    status: str
    overall_summary: str | None
    findings: list[FindingDTO]
    agreements: list[str]
    disagreements: list[str]
    related_career_id: str | None
    source_availability: SourceAvailabilityDTO | None
    explanation: str | None
    stages: list[str]
    evidence_added: bool
    mission: MissionSnapshotDTO
    artifacts_updated: list[str]


class GitHubSkillRecordDTO(BaseModel):
    skill: str
    category: str
    evidence: str


class GitHubInvestigationRecordDTO(BaseModel):
    id: str
    url: str
    owner: str
    repo: str
    name: str
    description: str
    primary_language: str | None
    languages: list[str]
    topics: list[str]
    license: str | None
    stars: int
    forks: int
    last_activity: str | None
    skills: list[GitHubSkillRecordDTO]
    overall_summary: str
    project_purpose: str
    technical_complexity: str
    problem_solving: str
    code_organization: str
    technology_breadth: str
    documentation_quality: str
    learning_signals: str
    engineering_maturity: str
    research_orientation: str
    ai_ml_signals: str
    created_at: datetime


class GitHubInvestigationsResponse(BaseModel):
    investigations: list[GitHubInvestigationRecordDTO]


class DocumentInvestigationRecordDTO(BaseModel):
    id: str
    filename: str
    category: str
    owning_specialist: str
    title: str | None
    summary: str | None
    key_findings: list[str]
    structured_fields: dict[str, str]
    created_at: datetime


class DocumentInvestigationsResponse(BaseModel):
    investigations: list[DocumentInvestigationRecordDTO]


class CareerInvestigationRecordDTO(BaseModel):
    id: str
    question: str
    overall_summary: str
    findings: list[FindingDTO]
    related_career_id: str | None
    created_at: datetime


class CareerInvestigationsResponse(BaseModel):
    investigations: list[CareerInvestigationRecordDTO]


class HistoryItemDTO(BaseModel):
    id: str
    mission_name: str
    mission_type: str
    owning_specialist: str
    timestamp: datetime
    status: str
    artifact_id: str


class HistoryResponse(BaseModel):
    items: list[HistoryItemDTO]


class CareerEventsResponse(BaseModel):
    events: list[CareerEventDTO]


class BookExpertSessionRequest(BaseModel):
    mentor_id: str
    slot_start: datetime
    topic: str


class ExpertSessionBookingDTO(BaseModel):
    id: str
    mentor_id: str
    mentor_name: str
    slot_start: datetime
    topic: str
    created_at: datetime


class ExpertSessionBookingsResponse(BaseModel):
    bookings: list[ExpertSessionBookingDTO]


class RequestGuidanceRequest(BaseModel):
    mentor_id: str
    message: str


class GuidanceRequestDTO(BaseModel):
    id: str
    mentor_id: str
    mentor_name: str
    message: str
    status: str
    created_at: datetime


class GuidanceRequestsResponse(BaseModel):
    requests: list[GuidanceRequestDTO]


class SavedExpertsResponse(BaseModel):
    mentor_ids: list[str]


class RegisterForEventRequest(BaseModel):
    event_id: str


class EventRegistrationDTO(BaseModel):
    id: str
    event_id: str
    event_title: str
    created_at: datetime


class EventRegistrationsResponse(BaseModel):
    registrations: list[EventRegistrationDTO]


class HealthResponse(BaseModel):
    status: str = "ok"
