from datetime import datetime
from typing import Any, Literal

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


class CareerBranchDTO(BaseModel):
    name: str
    description: str


class CareerFAQDTO(BaseModel):
    question: str
    answer: str


class TrendSummaryDTO(BaseModel):
    """A lightweight cross-reference into Global Trends — see the full
    TrendDTO further down. Kept separate/minimal here so CareerDetailDTO
    doesn't need the full Trend shape just to link to one."""

    id: str
    title: str
    category: str
    summary: str


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


# -- Sprint 1 — Skill Knowledge Base (docs/AUREON_DATA_ARCHITECTURE.md §3) --
# Defined here, ahead of CareerDetailDTO, since that DTO references it below.


class SkillDTO(BaseModel):
    id: str
    name: str
    category: str
    description: str
    parent_skill_id: str | None
    related_skill_ids: list[str]
    evidence_types_that_count: list[str]


# -- Sprint 2 — Company Knowledge Base (docs/AUREON_DATA_ARCHITECTURE.md §5) --
# Also defined here, ahead of CareerDetailDTO, for the same forward-reference reason.


class CompanyDTO(BaseModel):
    id: str
    name: str
    organization_kind: str
    industry: str
    size_category: str | None
    what_they_do: str
    logo_url: str | None
    hiring_focus_areas: list[str]
    notable_for: str


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
    #: Explore Batch 1 additions.
    description: str = ""
    why_people_love_it: str = ""
    branches: list[CareerBranchDTO] = []
    #: Never a recommendation — "you might also find this interesting."
    related_careers: list[CareerSummaryDTO] = []
    #: The single top related career not yet in the student's real
    #: exploration history; honestly None once nothing related is left
    #: unseen, or when there's no student context at all.
    recommended_next_exploration: CareerSummaryDTO | None = None
    related_trends: list[TrendSummaryDTO] = []
    #: Explore Polish Batch additions — all additive/defaulted.
    day_in_the_life: str = ""
    weekly_routine: str = ""
    daily_tools: list[str] = []
    career_progression: list[str] = []
    related_industries: list[str] = []
    research_areas: list[str] = []
    companies: list[str] = []
    universities: list[str] = []
    scholarships: list[str] = []
    competitions: list[str] = []
    books: list[str] = []
    communities: list[str] = []
    open_source_projects: list[str] = []
    certifications: list[str] = []
    projects: list[str] = []
    videos: list[str] = []
    common_misconceptions: list[str] = []
    faqs: list[CareerFAQDTO] = []
    #: Cross-field realistic transitions — deliberately separate from
    #: `related_careers` above (same-field/tag-overlap computation).
    adjacent_careers: list[str] = []
    #: Sprint 1 — real Skill entities resolved from Career.required_skill_ids
    #: (never a raw id list — the frontend renders these as real linked
    #: chips). Additive alongside `reality.required_skills`, which stays
    #: untouched as the display fallback for any career not yet backfilled.
    required_skills: list[SkillDTO] = []
    #: Sprint 2 — real Company entities resolved from Career.company_ids,
    #: additive alongside the existing `companies` string list above.
    hiring_companies: list[CompanyDTO] = []


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


class LinkRefDTO(BaseModel):
    label: str
    url: str


class CareerJourneyMilestoneDTO(BaseModel):
    stage: str
    label: str
    description: str
    year_label: str


class ExpertSummaryDTO(BaseModel):
    """Connect Batch 1 — Expert Connect's list-view shape. Same
    underlying `Mentor` row as `MentorSummaryDTO`, but Expert-named and
    surfacing the richer profile fields this batch adds."""

    id: str
    name: str
    profession: str
    specialization: str
    country: str
    city: str
    years_experience: int
    industries: list[str]
    organization: str
    trait_tags: list[str]
    who_should_talk_to_me: list[str]
    photo_url: str | None = None
    updated_at: datetime


class ExpertDetailDTO(BaseModel):
    id: str
    name: str
    role_type: str
    profession: str
    specialization: str
    field: str
    bio: str
    country: str
    city: str
    industries: list[str]
    education: list[str]
    organization: str
    current_role: str
    years_experience: int
    languages: list[str]
    photo_url: str | None = None
    who_should_talk_to_me: list[str]
    trait_tags: list[str]
    learning_style_fit: str
    linked_careers: list[CareerSummaryDTO]
    #: Career Journey.
    career_journey: list[CareerJourneyMilestoneDTO]
    #: Reality.
    day_in_the_life: str
    weekly_routine: str
    biggest_challenges: list[str]
    favourite_part: str
    biggest_misconceptions: list[str]
    what_surprised_them: str
    biggest_mistake: str
    one_regret: str
    salary_reality: str
    work_life_balance: str
    advice_for_beginners: str
    advice_for_parents: str
    faqs: list[CareerFAQDTO]
    #: Knowledge.
    projects: list[str]
    research: list[str]
    certifications: list[str]
    conferences: list[str]
    organizations: list[str]
    volunteer_work: list[str]
    portfolio_links: list[LinkRefDTO]
    social_links: list[LinkRefDTO]
    daily_skills: list[str]
    daily_tools: list[str]
    recommended_books: list[str]
    recommended_communities: list[str]
    suggested_books: list[str]
    suggested_companies: list[str]
    suggested_certifications: list[str]
    #: Reused Mentor detail logic — same honest, never-fabricated
    #: deterministic slots + real seeded career talks as `/mentors/{id}`.
    available_slots: list[datetime]
    upcoming_career_talks: list[CareerEventDTO]
    updated_at: datetime
    #: Connect Batch 2 — Mentorship. Both fields already existed on
    #: `Mentor` since Connect Batch 1 (forward-looking, unused until
    #: now); surfaced here for the first time, not newly added.
    accepts_mentorship: bool = False
    max_students: int = 0
    current_mentee_count: int = 0


class ExpertSearchResponse(BaseModel):
    experts: list[ExpertSummaryDTO]
    total: int
    limit: int
    offset: int


class ExpertFiltersResponse(BaseModel):
    specializations: list[str]
    industries: list[str]
    countries: list[str]


class ParentExpertAdviceDTO(BaseModel):
    expert_id: str
    expert_name: str
    expert_profession: str
    advice_for_parents: str
    faqs: list[CareerFAQDTO]


class ParentCareerViewDTO(BaseModel):
    career_id: str
    career_name: str
    one_liner: str
    required_education: str
    salary_ranges: list[SalaryRangeDTO]
    demand_2030: str
    demand_2035: str
    demand_2040: str
    common_misconceptions: list[str]
    earning_reality: str
    career_stability: str
    work_life_balance: str
    growth_opportunities: str
    educational_pathways: list[str]
    alternative_routes: list[str]
    global_demand: str
    risks: list[str]
    opportunities: list[str]
    expert_advice: list[ParentExpertAdviceDTO]


class ParentQuestionDTO(BaseModel):
    id: str
    category: str
    career_id: str | None
    question: str
    expert_response: str
    responding_expert_id: str | None
    is_seeded: bool
    created_at: datetime


class ParentQuestionsResponse(BaseModel):
    questions: list[ParentQuestionDTO]


class SharedSessionNoteDTO(BaseModel):
    id: str
    session_id: str
    author_role: str
    note: str
    created_at: datetime


class SharedSessionDTO(BaseModel):
    id: str
    student_id: str
    mentor_id: str
    career_id: str | None
    access_token: str
    participant_label: str
    topic: str
    status: str
    scheduled_slot: datetime | None
    created_at: datetime
    updated_at: datetime


class SharedSessionWithNotesDTO(SharedSessionDTO):
    notes: list[SharedSessionNoteDTO]


class CreateSharedSessionRequest(BaseModel):
    mentor_id: str
    career_id: str | None = None
    topic: str


class SharedSessionsResponse(BaseModel):
    sessions: list[SharedSessionDTO]


class JoinSharedSessionRequest(BaseModel):
    participant_label: str


class AddSharedSessionNoteRequest(BaseModel):
    author_role: str
    note: str


class LinkedExpertRefDTO(BaseModel):
    id: str
    name: str
    profession: str


class JourneyStoryDTO(BaseModel):
    """Connect Batch 2 — a Journey Story is a ``CareerStory`` read
    through a richer, honesty-labeled lens (see ``career.py``'s
    ``story_type``/``source_reference``). Deliberately not the same
    shape as ``CareerStoryDTO`` (Career detail's nested summary) — this
    is the full standalone view."""

    id: str
    career_id: str
    career_name: str
    person_label: str
    background: str
    journey: str
    challenges: str
    turning_points: str
    advice: str
    lessons_learned: str
    trait_tags: list[str]
    timeline: list[CareerJourneyMilestoneDTO]
    career_switch: bool
    gap_year: bool
    uncertainty_period: str
    current_outcome: str
    industry: str
    story_type: str
    source_reference: str
    discovery_themes: list[str] = []
    linked_expert: LinkedExpertRefDTO | None = None
    linked_life_mission_name: str | None = None


class JourneyStorySearchResponse(BaseModel):
    stories: list[JourneyStoryDTO]
    total: int
    limit: int
    offset: int


class JourneyStoryFiltersResponse(BaseModel):
    industries: list[str]
    careers: list[CareerSummaryDTO]
    discovery_themes: list[str] = []


class ReflectOnJourneyStoryRequest(BaseModel):
    prompt: str
    response: str


class ReflectOnJourneyStoryResponse(BaseModel):
    recorded: bool = True


class RelevantJourneyStoriesResponse(BaseModel):
    """"Stories You May Relate To" — deliberately not the same shape as
    ``JourneyStorySearchResponse`` (no total/limit/offset pagination —
    this is always a small, personalized, unpaginated list)."""

    stories: list[JourneyStoryDTO]


class KnowledgeCircleSummaryDTO(BaseModel):
    id: str
    name: str
    overview: str


class KnowledgeCircleViewDTO(BaseModel):
    """Connect Batch 2 — composed at read time from the linked
    ``CareerWorld``, ``TopicResourceDomain``(s), matching careers,
    trends, and life missions. Every list here is a merge of real
    already-seeded content, never re-authored."""

    id: str
    name: str
    overview: str
    what_this_field_is_about: str
    beginner_roadmap: list[str]
    beginner_projects: list[str]
    advanced_projects: list[str]
    laboratories: list[str]
    startups: list[str]
    ngos: list[str]
    scholarships: list[str]
    books: list[str]
    documentaries: list[str]
    podcasts: list[str]
    youtube_channels: list[str]
    journals_and_newsletters: list[str]
    conferences: list[str]
    competitions: list[str]
    hackathons: list[str]
    workshops: list[str]
    communities: list[str]
    open_source_projects: list[str]
    research_organizations: list[str]
    museums: list[str]
    companies: list[str]
    universities: list[str]
    internships: list[str]
    certifications: list[str]
    research_papers: list[str]
    government_initiatives: list[str]
    volunteering_opportunities: list[str]


class CircleResourceProgressDTO(BaseModel):
    id: str
    circle_id: str
    resource_type: str
    resource_label: str
    status: str
    updated_at: datetime


class CircleProgressResponse(BaseModel):
    progress: list[CircleResourceProgressDTO]


class ToggleCircleResourceRequest(BaseModel):
    resource_type: str
    resource_label: str


class MentorshipProgressNoteDTO(BaseModel):
    id: str
    author_role: str
    note: str
    created_at: datetime


class MentorshipDTO(BaseModel):
    id: str
    student_id: str
    expert_id: str
    review_token: str
    status: str
    goals: str
    progress_notes: list[MentorshipProgressNoteDTO]
    created_at: datetime
    updated_at: datetime
    #: Connect restructuring — resolved server-side from the real Mentor
    #: record so "My Mentors" can show expert identity without the
    #: frontend needing a second lookup. Empty strings when the expert
    #: record wasn't available to resolve (never fabricated).
    expert_name: str = ""
    expert_role: str = ""
    expert_domain: str = ""


class RequestMentorshipRequest(BaseModel):
    expert_id: str
    goals: str = ""


class MentorshipsResponse(BaseModel):
    mentorships: list[MentorshipDTO]


class AddMentorshipNoteRequest(BaseModel):
    author_role: str
    note: str


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


class EntranceExamDTO(BaseModel):
    id: str
    name: str
    description: str
    eligibility: list[str]
    preparation_guidance: str
    typical_timeline: str


class InstitutionSummaryDTO(BaseModel):
    id: str
    name: str
    country: str
    city: str
    trait_tags: list[str]
    is_partner: bool


class InstitutionReviewDTO(BaseModel):
    role_label: str
    quote: str
    sentiment: str


class InstitutionProfileDTO(BaseModel):
    """Not a ranking — a real, deterministic count-to-tier summary. See
    domain/services/institution_profile.py."""

    research: int
    entrepreneurship: int
    campus_life: int
    international_exposure: int


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
    #: Explore Batch 1 — merged Entrance Hub content, no separate route.
    campus_life_and_culture: str = ""
    fees_summary: str = ""
    scholarships_summary: str = ""
    entrance_exams: list[EntranceExamDTO] = []
    #: Explore Polish Batch additions.
    hostels: list[str] = []
    exchange_programs: list[str] = []
    campus_facilities: list[str] = []
    student_reviews: list[InstitutionReviewDTO] = []
    profile: InstitutionProfileDTO | None = None


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


# ---------------------------------------------------------------------------
# Discover Batch 1 backend migration — adaptive onboarding, World Signals,
# Uncertainty Signals, Orbit Status, Progressive Discovery.
# ---------------------------------------------------------------------------


class OnboardingRequest(BaseModel):
    """Request DTO for POST /v1/students/{student_id}/onboarding."""

    name: str | None = None
    age: int | None = None
    stage: Literal["School", "College", "Professional"] | None = None
    location_state: str | None = None
    location_city: str | None = None
    preferred_language: str | None = None
    current_situation: Literal["no_idea", "few_careers", "dream_career", "switch_careers"] | None = None
    worlds: list[str] = []
    worlds_unsure: bool = False


class WorldSignalDTO(BaseModel):
    world: str
    confidence: float
    evidence: list[str]
    status: str
    first_observed: datetime
    last_reinforced: datetime


class OrbitStatusDTO(BaseModel):
    """Never a comparison against other students; never names a
    career/college. ``confidence`` is the same real, already-capped
    ``StudentProfile.confidence_score`` — not a new metric."""

    current_orbit: str
    focus: list[str]
    avoid: list[str]
    explanation: str
    message: str
    confidence: float


class PendingCheckInDTO(BaseModel):
    world: str
    prompt: str
    options: list[str]


class ExperimentSummaryDTO(BaseModel):
    """Discover Batch 2 — a lightweight cross-reference into Career
    Experiments, used by ProgressiveDiscoveryStateResponse's
    ``suggested_experiment``. See the full ExperimentDTO further down."""

    id: str
    title: str
    related_world: str
    estimated_minutes: int


class ProgressiveDiscoveryStateResponse(BaseModel):
    """Response DTO for the onboarding submit route, the
    progressive-discovery GET, and the Curiosity Check-in answer route —
    the same shape from all three so the frontend never needs a second
    round trip to know what to show next."""

    onboarding_completed: bool
    orbit_status: OrbitStatusDTO
    pending_curiosity_checkin: PendingCheckInDTO | None
    world_signals: list[WorldSignalDTO]
    #: Discover Batch 2 — the single next real, uncompleted experiment to
    #: try, honestly None once nothing's left or when the route omits the
    #: catalog (see domain/services/progressive_discovery.py).
    suggested_experiment: ExperimentSummaryDTO | None = None


class CuriosityCheckInAnswerRequest(BaseModel):
    """Request DTO for POST /v1/students/{student_id}/curiosity-checkins/answer."""

    world: str
    chosen_options: list[str]


# ---------------------------------------------------------------------------
# Explore Batch 1 — Global Trends.
# ---------------------------------------------------------------------------


class TrendDTO(BaseModel):
    id: str
    title: str
    category: str
    summary: str
    description: str
    affected_industries: list[str]
    affected_skills: list[str]
    regions: list[str]
    time_horizon: str
    source_note: str
    #: Explore Polish Batch additions.
    key_milestones: list[str] = []
    countries_leading: list[str] = []
    affected_careers: list[str] = []
    research_papers: list[str] = []
    companies: list[str] = []
    startups: list[str] = []
    government_initiatives: list[str] = []
    risks: list[str] = []
    opportunities: list[str] = []


class TrendsResponse(BaseModel):
    trends: list[TrendDTO]


class FutureSkillDTO(BaseModel):
    skill: str
    mentioned_in_trend_count: int
    related_trend_ids: list[str]


class SkillsResponse(BaseModel):
    skills: list[SkillDTO]


class SkillDetailResponse(BaseModel):
    skill: SkillDTO
    #: Real careers requiring this skill, resolved live from
    #: Career.required_skill_ids — never stored/duplicated on Skill itself.
    careers_requiring_it: list[CareerSummaryDTO]


class CompaniesResponse(BaseModel):
    companies: list[CompanyDTO]


class CompanyDetailResponse(BaseModel):
    company: CompanyDTO
    #: Real careers hiring from this company, resolved live from
    #: Career.company_ids — never stored/duplicated on Company itself.
    careers_hiring_from_it: list[CareerSummaryDTO]


class FutureSkillsResponse(BaseModel):
    skills: list[FutureSkillDTO]


# ---------------------------------------------------------------------------
# Explore Batch 1 — Exposure Universe.
# ---------------------------------------------------------------------------


#: ExposureSuggestionDTO/ExposureUniverseResponse moved to the end of this
#: file (Exposure Universe merge batch) — they now reference CareerWorldDTO
#: and other DTOs defined later in the file; see the note there.


class ExposureInteractionRequest(BaseModel):
    career_id: str
    interaction: Literal["opened", "dismissed"]


class ExposureInteractionResponse(BaseModel):
    recorded: bool = True


# ---------------------------------------------------------------------------
# Explore Batch 1 — Opportunity Equality.
# ---------------------------------------------------------------------------


class OpportunitySummaryDTO(BaseModel):
    id: str
    title: str
    category: str
    organization: str
    description: str
    location: str
    is_remote: bool
    application_deadline: datetime | None
    official_link: str


class OpportunityEqualityRecommendationDTO(BaseModel):
    opportunity: OpportunitySummaryDTO
    readiness_label: str
    likelihood_of_self_discovery: str
    why_shown: str
    contributing_factors: list[str]


class OpportunityEqualityResponse(BaseModel):
    recommendations: list[OpportunityEqualityRecommendationDTO]


class OpportunityEqualityInteractionRequest(BaseModel):
    opportunity_id: str
    interaction: Literal["viewed", "saved"]


class OpportunityEqualityInteractionResponse(BaseModel):
    recorded: bool = True


# ---------------------------------------------------------------------------
# Discover Batch 2 — Career Experiments.
# ---------------------------------------------------------------------------


class ExperimentDTO(BaseModel):
    id: str
    title: str
    category: str
    description: str
    instructions: str
    estimated_minutes: int
    age_appropriate_note: str
    related_world: str
    target_traits: list[str]
    related_life_mission_ids: list[str] = []
    reflection_prompt: str
    source_note: str


class ExperimentsResponse(BaseModel):
    experiments: list[ExperimentDTO]
    #: Lets the frontend show completion status without a second round trip.
    completed_experiment_ids: list[str]


class ExperimentEvidenceRequest(BaseModel):
    """Structured self-report, not a score — see
    domain/models/experiment.py::ExperimentEvidence."""

    enjoyment: bool = False
    curiosity: bool = False
    frustration: bool = False
    persistence: bool = False
    confidence: bool = False
    reflection: str = ""


class ExperimentEvidenceDTO(BaseModel):
    enjoyment: bool
    curiosity: bool
    frustration: bool
    persistence: bool
    confidence: bool
    reflection: str


class ExperimentCompletionDTO(BaseModel):
    id: str
    experiment_id: str
    experiment_title: str
    related_world: str
    completed_at: datetime
    evidence: ExperimentEvidenceDTO


# ---------------------------------------------------------------------------
# Discover Batch 2 — Talent Discovery Lab.
# ---------------------------------------------------------------------------


class TalentEvidenceItemDTO(BaseModel):
    source: str
    description: str
    observed_at: datetime


class TalentPatternDTO(BaseModel):
    talent: str
    tier: str
    explanation: str
    evidence: list[TalentEvidenceItemDTO]


class TalentsResponse(BaseModel):
    patterns: list[TalentPatternDTO]


# ---------------------------------------------------------------------------
# Discover Navigation Refactor — Hidden Potential becomes the single
# canonical backend source for strengths/potential/evidence. Composes
# (never duplicates) HiddenPotentialPatternDTO/TalentPatternDTO/
# ExperimentSummaryDTO above. GET /talents stays live as a deprecated
# compatibility endpoint; this is the new canonical response.
# ---------------------------------------------------------------------------


class StrengthsGroupDTO(BaseModel):
    """A pure regrouping of analyze_talents' own tier field — no new
    scoring. still_discovering/emerging/growing are the real backend
    values; these are just this response's field names."""

    emerging: list[TalentPatternDTO]
    growing: list[TalentPatternDTO]
    consistently_observed: list[TalentPatternDTO]


class EvidenceTimelineItemDTO(BaseModel):
    source: str
    description: str
    observed_at: datetime
    talent: str


class DiscoveryStatisticsDTO(BaseModel):
    traits_tracked: int
    traits_with_strong_evidence: int
    hidden_patterns_found: int
    strengths_found: int
    experiments_completed: int


class HiddenPotentialResponse(BaseModel):
    hidden_patterns: list[HiddenPotentialPatternDTO]
    strengths: StrengthsGroupDTO
    suggested_experience: ExperimentSummaryDTO | None
    evidence_timeline: list[EvidenceTimelineItemDTO]
    discovery_statistics: DiscoveryStatisticsDTO


# ---------------------------------------------------------------------------
# Discover Batch 4 — Missing Worlds.
# ---------------------------------------------------------------------------


class CareerWorldDTO(BaseModel):
    id: str
    name: str
    description: str
    why_it_matters: str
    global_importance: str
    future_growth: str
    famous_careers: list[str]
    beginner_roadmap: list[str]
    required_skills: list[str]
    misconceptions: list[str]
    related_industries: list[str]
    videos: list[str]
    books: list[str]
    communities: list[str]
    beginner_projects: list[str]
    internships: list[str]
    colleges: list[str]
    companies: list[str]
    source_note: str


class WorldExplorationDTO(BaseModel):
    world: CareerWorldDTO
    exploration_level: str
    match_count: int


class MissingWorldsResponse(BaseModel):
    worlds: list[WorldExplorationDTO]
    recommended_next: list[str]


# ---------------------------------------------------------------------------
# Discover Batch 4 — Life Missions.
# ---------------------------------------------------------------------------


class LifeMissionDTO(BaseModel):
    id: str
    name: str
    description: str
    famous_people: list[str]
    organizations: list[str]
    companies: list[str]
    nonprofits: list[str]
    books: list[str]
    documentaries: list[str]
    podcasts: list[str]
    communities: list[str]
    real_world_examples: list[str]
    suggested_careers: list[str]
    projects: list[str]
    volunteering_opportunities: list[str]
    research_areas: list[str]
    startup_ideas: list[str]
    source_note: str


class MissionEvidenceItemDTO(BaseModel):
    source: str
    description: str
    observed_at: datetime


class MissionResonanceDTO(BaseModel):
    mission: LifeMissionDTO
    tier: str
    trend: str
    explanation: str
    evidence: list[MissionEvidenceItemDTO]


class LifeMissionsResponse(BaseModel):
    resonances: list[MissionResonanceDTO]
    other_missions: list[LifeMissionDTO]


# ---------------------------------------------------------------------------
# Experience Lab / Life Missions merge — Experience Lab becomes the single
# surviving Discover destination, with Life Mission resonance surfaced as
# "Your Emerging Missions" inside it rather than as its own nav item. This
# is a composition of the two DTO blocks above (ExperimentDTO/
# ExperimentCompletionDTO and LifeMissionDTO/MissionResonanceDTO) — neither
# domain's DTOs are duplicated or replaced.
# ---------------------------------------------------------------------------


class EmergingMissionDTO(BaseModel):
    mission: LifeMissionDTO
    tier: str
    trend: str
    explanation: str
    evidence: list[MissionEvidenceItemDTO]
    suggested_experience: ExperimentDTO | None


class ExperienceLabViewResponse(BaseModel):
    recommended: list[ExperimentDTO]
    mission_experiences: list[ExperimentDTO]
    career_experiences: list[ExperimentDTO]
    completed: list[ExperimentCompletionDTO]
    completed_experiment_ids: list[str]
    emerging_missions: list[EmergingMissionDTO]


# ---------------------------------------------------------------------------
# Discover Batch 5 — Learning Style Discovery.
# ---------------------------------------------------------------------------


class LearningStyleDTO(BaseModel):
    id: str
    name: str
    description: str
    strengths: list[str]
    excels_in: list[str]
    common_struggles: list[str]
    study_strategies: list[str]
    note_taking_techniques: list[str]
    memory_strategies: list[str]
    active_learning_methods: list[str]
    project_ideas: list[str]
    practice_routines: list[str]
    collaboration_techniques: list[str]
    learning_environments: list[str]
    productivity_systems: list[str]
    recommended_books: list[str]
    research_backed_resources: list[str]
    online_courses: list[str]
    communities: list[str]
    ways_to_strengthen: list[str]
    source_note: str


class LearningStyleEvidenceItemDTO(BaseModel):
    source: str
    description: str
    observed_at: datetime


class LearningStylePatternDTO(BaseModel):
    style: LearningStyleDTO
    tier: str
    explanation: str
    evidence: list[LearningStyleEvidenceItemDTO]
    recommended_experiments: list[ExperimentDTO]


class LearningStylesResponse(BaseModel):
    patterns: list[LearningStylePatternDTO]


# ---------------------------------------------------------------------------
# Relevant Interests — a plain, evidence-grounded signal of real recurring
# student interest, consumed by Decision Lab's "Relevant Interests"
# strength card and its "Interest alignment" comparison dimension.
# ---------------------------------------------------------------------------


class InterestEvidenceItemDTO(BaseModel):
    source: str
    description: str
    observed_at: datetime


class RelevantInterestDTO(BaseModel):
    topic: str
    explanation: str
    evidence: list[InterestEvidenceItemDTO]


# ---------------------------------------------------------------------------
# Decide Batch 1 — Decision Workspace. Composes ~13 existing systems into
# one per-career card; every nested DTO below is an existing type reused
# verbatim (ExpertSummaryDTO, JourneyStoryDTO, KnowledgeCircleSummaryDTO,
# TalentPatternDTO, RelevantInterestDTO, LearningStylePatternDTO,
# MissionResonanceDTO, CareerWorldDTO, OpportunityEqualityRecommendationDTO,
# SalaryRangeDTO) — nothing here duplicates a shape that already exists.
# Placed at the end of the file since it references nearly every DTO
# defined above it.
# ---------------------------------------------------------------------------


class DecisionExplanationDTO(BaseModel):
    supporting_by_source: dict[str, list[str]]
    contradicting_by_source: dict[str, list[str]]
    missing_evidence: list[str]
    strength_traits: list[str]


class ReadinessCheckpointsDTO(BaseModel):
    has_reflection: bool
    has_experiment: bool
    has_expert_contact: bool
    has_explored_world: bool
    has_explored_opportunity: bool
    has_simulation: bool
    has_knowledge_circle_engagement: bool
    percent: int


class RealityCheckDTO(BaseModel):
    daily_work: str
    work_life_balance: str
    stress: str
    automation_risk: str
    remote_possibility: str
    travel: str
    industry_outlook: str
    salary_ranges: list[SalaryRangeDTO]


class CardRecommendationDTO(BaseModel):
    verdict: str
    reason: str


class NextActionItemDTO(BaseModel):
    label: str
    href: str | None = None


class CareerDecisionCardDTO(BaseModel):
    # Overview
    career_id: str
    career_name: str
    one_liner: str
    why_it_matters: str
    confidence_label: str
    confidence_band: str
    demand_2030: str
    demand_2035: str
    demand_2040: str
    readiness: ReadinessCheckpointsDTO
    # Reality Check
    reality_check: RealityCheckDTO
    # Evidence
    reasons_for: list[str]
    reasons_against: list[str]
    missing_evidence: list[str]
    explanation: DecisionExplanationDTO
    # Strengths
    hidden_strengths: list[TalentPatternDTO]
    relevant_interests: list[RelevantInterestDTO]
    learning_style_pattern: LearningStylePatternDTO | None = None
    # Explore
    unexplored_worlds: list[CareerWorldDTO]
    related_life_missions: list[MissionResonanceDTO]
    top_journey_stories: list[JourneyStoryDTO]
    top_knowledge_circles: list[KnowledgeCircleSummaryDTO]
    top_opportunities: list[OpportunityEqualityRecommendationDTO]
    # People
    top_experts: list[ExpertSummaryDTO]
    # Your Next Step
    decision_gaps: list[str]
    next_actions: list[NextActionItemDTO]
    recommendation: CardRecommendationDTO


class StageProgressDTO(BaseModel):
    discover: bool
    explore: bool
    connect: bool


class DecisionWorkspaceResponse(BaseModel):
    cards: list[CareerDecisionCardDTO]
    workspace_gaps: list[str]
    overall_readiness_percent: int
    stage_progress: StageProgressDTO


# --- Suggest to Aureon --------------------------------------------------


class CreateSuggestionRequest(BaseModel):
    category: str
    title: str
    description: str
    source_url: str | None = None
    context_type: str | None = None
    context_id: str | None = None
    context_metadata: dict[str, Any] | None = None


class SuggestionDTO(BaseModel):
    id: str
    student_id: str
    category: str
    title: str
    description: str
    source_url: str | None
    context_type: str | None
    context_id: str | None
    context_metadata: dict[str, Any]
    status: str
    review_notes: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SuggestionsResponse(BaseModel):
    suggestions: list[SuggestionDTO]


class UpdateSuggestionStatusRequest(BaseModel):
    status: str
    review_notes: str | None = None


# --- Exposure Universe merge (Missing Worlds + Exposure Universe) -------
# Placed here, after CareerWorldDTO/CareerSummaryDTO/KnowledgeCircleSummaryDTO/
# JourneyStoryDTO/ExpertSummaryDTO are already defined, for the same
# forward-reference reason Decide Batch 1's DTOs live at the end of this
# file — Pydantic model fields are resolved at class-definition time here
# (no `from __future__ import annotations`).


class WorldExposureSummaryDTO(BaseModel):
    world_name: str
    level: str


class ExposureMapDTO(BaseModel):
    engaged: list[WorldExposureSummaryDTO]
    limited_or_none: list[WorldExposureSummaryDTO]


class MissingWorldCardDTO(BaseModel):
    world: CareerWorldDTO
    level: str
    match_count: int
    why_missing: str
    related_careers: list[CareerSummaryDTO]
    linked_circle: KnowledgeCircleSummaryDTO | None


class ExposureSuggestionDTO(BaseModel):
    """Never a fit score, never a percentage — framed entirely around
    "have you seen this?", not "you'd be good at this."."""

    career: CareerSummaryDTO
    curiosity_hook: str
    #: Explore Polish Batch additions — composed entirely from the
    #: (already-enriched) Career catalog, plus one reused Experience Lab
    #: suggestion. See domain/services/exposure_recommendation.py.
    mini_introduction: str = ""
    quick_project: str | None = None
    watch: list[str] = []
    read: list[str] = []
    build: list[str] = []
    join: list[str] = []
    reflect_prompt: str = ""
    suggested_experience: ExperimentSummaryDTO | None = None
    #: Exposure Universe merge — set when this suggestion's industry
    #: overlaps a currently-recommended Missing World, so the frontend can
    #: visually connect "this possibility relates to a world you haven't
    #: explored." None when no such overlap exists — never fabricated.
    related_missing_world: str | None = None


class ExposureUniverseResponse(BaseModel):
    exposure_map: ExposureMapDTO
    missing_worlds: list[MissingWorldCardDTO]
    suggestions: list[ExposureSuggestionDTO]


class WorldRelatedStoryDTO(BaseModel):
    """A lightweight preview, not the full Journey Story view (which needs
    `build_journey_story_view` plus expert/mission lookups) — proportionate
    for a "related stories" preview that links out to the real Journey
    Stories screen for the complete read."""

    id: str
    career_id: str
    career_name: str
    person_label: str
    journey: str
    advice: str


class WorldExplorationDetailDTO(BaseModel):
    world: CareerWorldDTO
    level: str
    match_count: int
    why_missing: str
    related_careers: list[CareerSummaryDTO]
    related_stories: list[WorldRelatedStoryDTO]
    related_experts: list[ExpertSummaryDTO]
    linked_circle: KnowledgeCircleSummaryDTO | None
