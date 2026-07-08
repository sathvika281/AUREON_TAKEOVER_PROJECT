// Mirrors backend/src/aureon/shared/schemas.py — keep in sync by hand until
// a shared schema-generation step is introduced.

export interface HealthResponse {
  status: string;
}

export interface ConversationTurnRequest {
  student_id: string;
  conversation_id: string | null;
  message: string;
}

export interface TraitSignal {
  score: number | null;
  summary: string;
}

export interface CareerHypothesis {
  career_name: string;
  confidence: number;
  status: string;
  transition_reason: string | null;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  missing_evidence: string[];
}

export interface SuggestedActivity {
  title: string;
  description: string;
  reason: string;
}

export interface ReflectionEntry {
  prompt: string;
  response: string | null;
  created_at: string;
  answered_at: string | null;
}

/** One Discovery Notebook entry, server-persisted. `kind` determines
 * which fields are populated: "observation" uses text/source/
 * confidence_label/related_trait; "belief_revision" uses the four-part
 * previous_state/new_evidence/updated_belief/reason story. */
export interface NotebookEntry {
  id: string;
  kind: "observation" | "belief_revision";
  text: string;
  source: string;
  related_trait: string | null;
  related_hypothesis: string | null;
  related_career: string | null;
  confidence_label: string | null;
  previous_state: string | null;
  new_evidence: string | null;
  updated_belief: string | null;
  reason: string | null;
  created_at: string;
}

export interface EvidenceRecord {
  id: string;
  text: string;
  source: string;
  related_trait: string | null;
  related_hypothesis: string | null;
  related_career: string | null;
  relation: string;
  created_at: string;
}

export interface HiddenPotentialPattern {
  id: string;
  trait_a: string;
  trait_b: string;
  sentence: string;
  supporting_evidence: string[];
}

export interface ConversationTurnResponse {
  conversation_id: string;
  reply: string;
  mode: string;
  active_agent: string | null;
  confidence_score: number;
  understanding_stage: string;
  understanding_narrative: string;
  career_dna: Record<string, TraitSignal>;
  hypotheses: CareerHypothesis[];
  hidden_potential: HiddenPotentialPattern[];
  notebook_entries: NotebookEntry[];
  reflection_prompt: string | null;
  suggested_activity: SuggestedActivity | null;
}

export interface DiscoveryProfileResponse {
  student_id: string;
  confidence_score: number;
  understanding_stage: string;
  understanding_narrative: string;
  career_dna: Record<string, TraitSignal>;
  hypotheses: CareerHypothesis[];
  hidden_potential: HiddenPotentialPattern[];
  notebook_entries: NotebookEntry[];
  evidence_graph: EvidenceRecord[];
  reflection_journal: ReflectionEntry[];
}

// ---------------------------------------------------------------------------
// Phase 2 — Explore Careers
// ---------------------------------------------------------------------------

export interface SalaryRange {
  region: string;
  range: string;
  note: string;
}

export interface CareerReality {
  daily_work: string;
  work_environment: string;
  collaboration_level: string;
  creativity_level: string;
  research_intensity: string;
  learning_curve: string;
  travel: string;
  remote_possibility: string;
  stress_factors: string;
  typical_challenges: string;
  misconceptions: string;
  long_term_growth: string;
  salary_ranges: SalaryRange[];
  required_education: string;
  required_skills: string[];
  entrepreneurship_potential: string;
}

export interface FutureLens {
  ai_impact: string;
  automation_risk: string;
  demand_2030: string;
  demand_2035: string;
  demand_2040: string;
  emerging_opportunities: string;
  skills_becoming_valuable: string[];
  timeline_narrative: string;
}

export interface CareerSummary {
  id: string;
  name: string;
  category: string;
  industry: string;
  countries: string[];
  one_liner: string;
  trait_tags: string[];
}

export interface CareerStory {
  id: string;
  career_id: string;
  person_label: string;
  background: string;
  journey: string;
  challenges: string;
  turning_points: string;
  advice: string;
  lessons_learned: string;
  relevant_to_student: boolean;
}

export interface CareerDetail {
  id: string;
  name: string;
  category: string;
  industry: string;
  countries: string[];
  one_liner: string;
  trait_tags: string[];
  reality: CareerReality;
  future_lens: FutureLens;
  stories: CareerStory[];
}

/** No raw confidence number — only the qualitative Evidence Strength
 * label, same treatment as Career Hypotheses. */
export interface CareerCandidate {
  career_id: string;
  career_name: string;
  why_it_matches: string;
  evidence_strength: "Strong" | "Growing" | "Needs More Evidence";
  uncertainty_reason: string | null;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  missing_evidence: string[];
  is_shortlisted: boolean;
}

export interface CareerCandidatesResponse {
  candidates: CareerCandidate[];
  insufficient_evidence: boolean;
  insufficient_evidence_reason: string | null;
  /** V13 — real, deterministic pulls from the student's own already-run
   * Mentor Match/Institution Match analysis. Never fabricated. */
  recommended_colleges: string[];
  recommended_experts: string[];
}

export type CareerInteractionType =
  | "opened"
  | "revisited"
  | "bookmarked"
  | "removed"
  | "story_viewed"
  | "future_lens_explored"
  | "reality_read"
  | "compared";

/** Observational only — never itself evidence. See
 * domain/models/career_exploration.py. */
export interface CareerExplorationEvent {
  id: string;
  career_id: string;
  interaction_type: CareerInteractionType;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface RecordCareerExplorationEventRequest {
  career_id: string;
  interaction_type: CareerInteractionType;
  metadata?: Record<string, unknown>;
}

export interface RecordCareerExplorationEventResponse {
  recorded: boolean;
}

export interface CareerExplorationHistoryResponse {
  events: CareerExplorationEvent[];
}

// ---------------------------------------------------------------------------
// Phase 3 — Decide Confidently
// ---------------------------------------------------------------------------

export interface MentorSummary {
  id: string;
  name: string;
  role_type: string;
  field: string;
  bio: string;
  trait_tags: string[];
  learning_style_fit: string;
  // V13 — Expert Connect additive fields.
  organization: string;
  years_experience: number;
  journey_highlights: string[];
  discussion_topics: string[];
}

export interface CareerEvent {
  id: string;
  title: string;
  event_type: "workshop" | "hackathon" | "open_day" | "career_talk";
  institution_id: string | null;
  mentor_id: string | null;
  description: string;
  scheduled_at: string;
}

export interface MentorDetail extends MentorSummary {
  available_slots: string[];
  upcoming_career_talks: CareerEvent[];
}

export interface ResearchLab {
  id: string;
  name: string;
  focus_area: string;
  description: string;
}

export interface StudentOrganization {
  id: string;
  name: string;
  focus_area: string;
  description: string;
}

export interface AcademicProgram {
  id: string;
  name: string;
  degree_type: string;
  field: string;
  description: string;
}

export interface InnovationCenter {
  id: string;
  name: string;
  focus_area: string;
  description: string;
}

export interface FacultyHighlight {
  id: string;
  name: string;
  title: string;
  expertise_area: string;
  bio: string;
}

export interface StudentAmbassador {
  id: string;
  student_label: string;
  program: string;
  message: string;
}

export interface StudentProject {
  id: string;
  student_label: string;
  project_title: string;
  description: string;
  skills_used: string[];
}

export interface InternshipOpportunity {
  id: string;
  title: string;
  field: string;
  description: string;
}

export interface InstitutionSummary {
  id: string;
  name: string;
  country: string;
  city: string;
  trait_tags: string[];
  is_partner: boolean;
}

export interface InstitutionDetail {
  id: string;
  name: string;
  country: string;
  city: string;
  research_culture: string;
  innovation_ecosystem: string;
  industry_collaboration: string;
  placements: string;
  learning_environment: string;
  trait_tags: string[];
  is_partner: boolean;
  research_labs: ResearchLab[];
  student_organizations: StudentOrganization[];
  academic_programs: AcademicProgram[];
  // V13 — College Collaboration additive sections.
  innovation_centers: InnovationCenter[];
  faculty_highlights: FacultyHighlight[];
  student_ambassadors: StudentAmbassador[];
  student_projects: StudentProject[];
  internship_opportunities: InternshipOpportunity[];
  upcoming_events: CareerEvent[];
}

/** No raw confidence number — same Evidence Strength treatment as Career
 * Candidates. */
export interface MentorMatch {
  mentor_id: string;
  mentor_name: string;
  why_it_matches: string;
  evidence_strength: "Strong" | "Growing" | "Needs More Evidence";
  uncertainty_reason: string | null;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  missing_evidence: string[];
}

export interface MentorMatchesResponse {
  matches: MentorMatch[];
  insufficient_evidence: boolean;
  insufficient_evidence_reason: string | null;
  mission: MissionSnapshot | null;
  artifacts_updated: string[];
}

export interface CollegeMatch {
  institution_id: string;
  institution_name: string;
  why_it_matches: string;
  evidence_strength: "Strong" | "Growing" | "Needs More Evidence";
  uncertainty_reason: string | null;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  missing_evidence: string[];
}

export interface CollegeMatchesResponse {
  matches: CollegeMatch[];
  insufficient_evidence: boolean;
  insufficient_evidence_reason: string | null;
  mission: MissionSnapshot | null;
  artifacts_updated: string[];
}

export interface ComparisonDimension {
  dimension: string;
  per_career: Record<string, string>;
  why_it_matters_to_you: string;
}

export interface CareerComparison {
  id: string;
  career_ids: string[];
  career_names: Record<string, string>;
  dimensions: ComparisonDimension[];
  summary_reason: string;
  missing_evidence: string[];
  created_at: string;
}

export interface CareerComparisonsResponse {
  comparisons: CareerComparison[];
  recommended_colleges: string[];
  recommended_experts: string[];
}

export interface ParallelUniverseBranch {
  career_id: string;
  career_name: string;
  daily_work: string;
  lifestyle: string;
  growth: string;
  challenges: string;
  future_opportunities: string;
}

export interface ParallelUniverseScenario {
  id: string;
  branches: ParallelUniverseBranch[];
  framing_note: string;
  missing_evidence: string[];
  created_at: string;
}

export interface ParallelUniverseResponse {
  scenarios: ParallelUniverseScenario[];
}

// ---------------------------------------------------------------------------
// V11 — Career Simulator & Decision Laboratory
// ---------------------------------------------------------------------------

export interface SimulatedJourneyPhase {
  phase: string;
  focus: string;
  milestones: string[];
}

export interface TradeOffAnalysis {
  advantages: string[];
  challenges: string[];
  opportunities: string[];
  sacrifices: string[];
  uncertainties: string[];
}

export interface CareerPathSimulation {
  career_id: string;
  career_name: string;
  required_skills: string;
  higher_education_path: string;
  work_environment: string;
  lifestyle: string;
  typical_challenges: string;
  growth_potential: string;
  risk_factors: string;
  research_opportunities: string;
  industry_opportunities: string;
  future_adaptability: string;
  career_dna_alignment: string;
  student_interest_alignment: string;
  evidence_confidence: string;
  learning_journey: string;
  expected_milestones: string[];
  timeline: SimulatedJourneyPhase[];
  trade_offs: TradeOffAnalysis;
  next_best_actions: string[];
}

export interface DecisionInsights {
  strongest_match_career_id: string | null;
  why: string;
  possible_risks: string[];
  questions_to_explore: string[];
  recommended_next_investigation: string;
  recommended_mentors: string[];
  recommended_institutions: string[];
  recommended_resources: string[];
}

export interface CareerSimulation {
  id: string;
  career_ids: string[];
  career_names: Record<string, string>;
  simulations: CareerPathSimulation[];
  decision_insights: DecisionInsights;
  missing_evidence: string[];
  created_at: string;
}

export interface CareerSimulationsResponse {
  simulations: CareerSimulation[];
  insufficient_evidence: boolean;
  insufficient_evidence_reason: string | null;
  mission: MissionSnapshot | null;
  artifacts_updated: string[];
}

export interface DecisionTimelineMilestone {
  kind: string;
  text: string;
  created_at: string;
}

export interface DecisionTimelineResponse {
  milestones: DecisionTimelineMilestone[];
  current_direction_summary: string;
}

export type DecisionMemoryActionType = "compared" | "shortlisted" | "removed";

export interface DecisionMemoryEntry {
  id: string;
  action_type: DecisionMemoryActionType;
  career_ids: string[];
  career_names: Record<string, string>;
  reason: string;
  created_at: string;
}

export interface DecisionMemoryResponse {
  entries: DecisionMemoryEntry[];
}

export type ProgressDirection = "improving" | "steady" | "slowing" | "not_enough_evidence";

export interface ProgressDimension {
  key: string;
  label: string;
  direction: ProgressDirection;
  evidence_summary: string[];
  reasoning: string;
}

export interface ProgressTimelineWindow {
  label: string;
  description: string;
  event_count: number;
}

export interface ProgressPriority {
  rank: number;
  action: string;
  evidence: string;
}

export interface ProgressReport {
  overall_narrative: string;
  dimensions: ProgressDimension[];
  growing_strengths: string[];
  areas_slowing_down: string[];
  recent_improvements: string[];
  timeline: ProgressTimelineWindow[];
  next_priorities: ProgressPriority[];
  insufficient_evidence: boolean;
  insufficient_evidence_reason: string | null;
  generated_at: string;
  mission: MissionSnapshot | null;
  artifacts_updated: string[];
}

// ---------------------------------------------------------------------------
// V7 — Mission Workspace. MissionSnapshot is Aureon's universal execution
// view: every mission-backed feature hands the same shape to the same
// MissionWorkspace component, regardless of what kind of mission it was.
// ---------------------------------------------------------------------------

export type AgentSnapshotStatus = "completed" | "not_required";

export interface AgentStatus {
  name: string;
  display_name: string;
  status: AgentSnapshotStatus;
}

export interface Delegation {
  from_agent: string;
  to_agent: string;
  capability: string;
  reason: string;
}

export interface MissionEvidence {
  source: string;
  summary: string;
  reliability: string | null;
  source_type: string | null;
  title: string | null;
  confidence: number | null;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface ToolExecution {
  tool_name: string;
  status: "completed" | "failed" | "not_connected";
  explanation: string | null;
  evidence: MissionEvidence[];
}

export interface MissionSnapshot {
  stages: string[];
  agents: AgentStatus[];
  delegations: Delegation[];
  tools: ToolExecution[];
  evidence: MissionEvidence[];
  narration: string[];
}

// ---------------------------------------------------------------------------
// V6/V7 — URL Intelligence
// ---------------------------------------------------------------------------

export interface UrlInvestigationResult {
  url: string;
  category: string;
  owning_specialist: string;
  delegated: boolean;
  status: "completed" | "failed" | "not_connected";
  title: string | null;
  summary: string | null;
  key_findings: string[];
  structured_fields: Record<string, string>;
  explanation: string | null;
  stages: string[];
  evidence_added: boolean;
  mission: MissionSnapshot;
  artifacts_updated: string[];
}

// ---------------------------------------------------------------------------
// V8 — Document Intelligence
// ---------------------------------------------------------------------------

export interface DocumentInvestigationResult {
  filename: string;
  category: string;
  owning_specialist: string;
  matched_on: "filename" | "content" | "default";
  status: "completed" | "failed" | "not_connected";
  title: string | null;
  summary: string | null;
  key_findings: string[];
  structured_fields: Record<string, string>;
  explanation: string | null;
  stages: string[];
  evidence_added: boolean;
  mission: MissionSnapshot;
  artifacts_updated: string[];
}

// ---------------------------------------------------------------------------
// V10 — Multi-Source Search Intelligence
// ---------------------------------------------------------------------------

export interface Finding {
  claim: string;
  status: "supported" | "contradicted" | "mixed" | "insufficient_evidence";
  citing_sources: string[];
  explanation: string;
}

/** Display-only — which real sources were actually reached. Never
 * reflects or influences the findings/overall_summary alongside it. */
export interface SourceStatus {
  name: string;
  category: string;
  reached: boolean;
  note: string | null;
}

export interface SourceAvailability {
  total_sources: number;
  sources_retrieved: number;
  sources_unavailable: number;
  sources: SourceStatus[];
}

export interface SearchInvestigationResult {
  question: string;
  status: "completed" | "failed" | "not_connected";
  overall_summary: string | null;
  findings: Finding[];
  agreements: string[];
  disagreements: string[];
  related_career_id: string | null;
  source_availability: SourceAvailability | null;
  explanation: string | null;
  stages: string[];
  evidence_added: boolean;
  mission: MissionSnapshot;
  artifacts_updated: string[];
}

// ---------------------------------------------------------------------------
// V9 — GitHub Intelligence (Discovery Agent's flagship capability)
// ---------------------------------------------------------------------------

export interface GitHubSkill {
  skill: string;
  category: string;
  evidence: string;
}

/** Metadata for display only — stars/forks/last_activity are shown
 * honestly but never influenced any reasoning or Career DNA update. */
export interface GitHubRepoSummary {
  name: string;
  description: string;
  owner: string;
  primary_language: string | null;
  languages: string[];
  topics: string[];
  license: string | null;
  stars: number;
  forks: number;
  last_activity: string | null;
}

export interface GitHubInvestigationResult {
  url: string;
  status: "completed" | "failed" | "not_connected";
  explanation: string | null;
  repo: GitHubRepoSummary | null;
  skills: GitHubSkill[];
  overall_summary: string | null;
  project_purpose: string | null;
  technical_complexity: string | null;
  problem_solving: string | null;
  code_organization: string | null;
  technology_breadth: string | null;
  documentation_quality: string | null;
  learning_signals: string | null;
  engineering_maturity: string | null;
  research_orientation: string | null;
  ai_ml_signals: string | null;
  stages: string[];
  evidence_added: boolean;
  mission: MissionSnapshot;
  artifacts_updated: string[];
}

// ---------------------------------------------------------------------------
// V12 — Authentication, User Identity & Investigation History
// ---------------------------------------------------------------------------

export interface GitHubInvestigationRecord {
  id: string;
  url: string;
  owner: string;
  repo: string;
  name: string;
  description: string;
  primary_language: string | null;
  languages: string[];
  topics: string[];
  license: string | null;
  stars: number;
  forks: number;
  last_activity: string | null;
  skills: GitHubSkill[];
  overall_summary: string;
  project_purpose: string;
  technical_complexity: string;
  problem_solving: string;
  code_organization: string;
  technology_breadth: string;
  documentation_quality: string;
  learning_signals: string;
  engineering_maturity: string;
  research_orientation: string;
  ai_ml_signals: string;
  created_at: string;
}

export interface GitHubInvestigationsResponse {
  investigations: GitHubInvestigationRecord[];
}

export interface DocumentInvestigationRecord {
  id: string;
  filename: string;
  category: string;
  owning_specialist: string;
  title: string | null;
  summary: string | null;
  key_findings: string[];
  structured_fields: Record<string, string>;
  created_at: string;
}

export interface DocumentInvestigationsResponse {
  investigations: DocumentInvestigationRecord[];
}

export interface CareerInvestigationRecord {
  id: string;
  question: string;
  overall_summary: string;
  findings: Finding[];
  related_career_id: string | null;
  created_at: string;
}

export interface CareerInvestigationsResponse {
  investigations: CareerInvestigationRecord[];
}

export interface HistoryItem {
  id: string;
  mission_name: string;
  mission_type: string;
  owning_specialist: string;
  timestamp: string;
  status: string;
  artifact_id: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
}

// ---------------------------------------------------------------------------
// V13 — Career Exploration Ecosystem (College Collaboration / Expert Connect)
// ---------------------------------------------------------------------------

export interface CareerEventsResponse {
  events: CareerEvent[];
}

export interface ExpertSessionBooking {
  id: string;
  mentor_id: string;
  mentor_name: string;
  slot_start: string;
  topic: string;
  created_at: string;
}

export interface ExpertSessionBookingsResponse {
  bookings: ExpertSessionBooking[];
}

export interface GuidanceRequestRecord {
  id: string;
  mentor_id: string;
  mentor_name: string;
  message: string;
  status: string;
  created_at: string;
}

export interface GuidanceRequestsResponse {
  requests: GuidanceRequestRecord[];
}

export interface SavedExpertsResponse {
  mentor_ids: string[];
}

export interface EventRegistrationRecord {
  id: string;
  event_id: string;
  event_title: string;
  created_at: string;
}

export interface EventRegistrationsResponse {
  registrations: EventRegistrationRecord[];
}
