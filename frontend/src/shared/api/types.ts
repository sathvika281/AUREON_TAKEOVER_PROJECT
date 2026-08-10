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
// Discover Batch 1 — adaptive onboarding, World Signals, Uncertainty
// Signals, Orbit Status, Progressive Discovery. Mirrors
// backend/src/aureon/shared/schemas.py's same-named DTOs.
// ---------------------------------------------------------------------------

export interface OnboardingRequest {
  name: string | null;
  age: number | null;
  stage: "School" | "College" | "Professional" | null;
  location_state: string | null;
  location_city: string | null;
  preferred_language: string | null;
  current_situation: "no_idea" | "few_careers" | "dream_career" | "switch_careers" | null;
  worlds: string[];
  worlds_unsure: boolean;
}

export interface WorldSignal {
  world: string;
  confidence: number;
  evidence: string[];
  status: "curious" | "reinforced";
  first_observed: string;
  last_reinforced: string;
}

export interface OrbitStatus {
  current_orbit: string;
  focus: string[];
  avoid: string[];
  explanation: string;
  message: string;
  confidence: number;
}

export interface PendingCheckIn {
  world: string;
  prompt: string;
  options: string[];
}

/** Discover Batch 2 — a lightweight cross-reference into Career
 * Experiments. See the full Experiment interface further down. */
export interface ExperimentSummary {
  id: string;
  title: string;
  related_world: string;
  estimated_minutes: number;
}

export interface ProgressiveDiscoveryState {
  onboarding_completed: boolean;
  orbit_status: OrbitStatus;
  pending_curiosity_checkin: PendingCheckIn | null;
  world_signals: WorldSignal[];
  /** The single next real, uncompleted experiment to try — honestly
   * null once nothing's left. */
  suggested_experiment: ExperimentSummary | null;
}

export interface CuriosityCheckInAnswerRequest {
  world: string;
  chosen_options: string[];
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

export interface CareerBranch {
  name: string;
  description: string;
}

export interface CareerFAQ {
  question: string;
  answer: string;
}

export interface TrendSummary {
  id: string;
  title: string;
  category: string;
  summary: string;
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
  // Explore Batch 1 additions.
  description: string;
  why_people_love_it: string;
  branches: CareerBranch[];
  related_careers: CareerSummary[];
  recommended_next_exploration: CareerSummary | null;
  related_trends: TrendSummary[];
  // Explore Polish Batch additions.
  day_in_the_life: string;
  weekly_routine: string;
  daily_tools: string[];
  career_progression: string[];
  related_industries: string[];
  research_areas: string[];
  companies: string[];
  universities: string[];
  scholarships: string[];
  competitions: string[];
  books: string[];
  communities: string[];
  open_source_projects: string[];
  certifications: string[];
  projects: string[];
  videos: string[];
  common_misconceptions: string[];
  faqs: CareerFAQ[];
  /** Cross-field realistic transitions (e.g. Software Engineer -> Product
   * Manager) — plain names, deliberately separate from `related_careers`. */
  adjacent_careers: string[];
  /** Sprint 1 — real Skill entities, additive alongside
   * `reality.required_skills` (left untouched as the display fallback for
   * any career not yet backfilled with real links). */
  required_skills: Skill[];
  /** Sprint 2 — real Company entities, additive alongside `companies`
   * above (left untouched as the display fallback). */
  hiring_companies: Company[];
  /** Sprint 3 — real Project entities that list this career in their own
   * related_career_ids (Project holds the edge, not Career). Named
   * distinctly from the existing plain-text `projects` field above so
   * the two never collide. */
  related_projects: Project[];
}

// -- Sprint 1 — Skill Knowledge Base (docs/AUREON_DATA_ARCHITECTURE.md §3) --

export interface Skill {
  id: string;
  name: string;
  category: string;
  description: string;
  parent_skill_id: string | null;
  related_skill_ids: string[];
  evidence_types_that_count: string[];
}

export interface SkillsResponse {
  skills: Skill[];
}

export interface SkillDetail {
  skill: Skill;
  careers_requiring_it: CareerSummary[];
}

// -- Sprint 2 — Company Knowledge Base (docs/AUREON_DATA_ARCHITECTURE.md §5) --

export interface Company {
  id: string;
  name: string;
  organization_kind: string;
  industry: string;
  size_category: string | null;
  what_they_do: string;
  logo_url: string | null;
  hiring_focus_areas: string[];
  notable_for: string;
}

export interface CompaniesResponse {
  companies: Company[];
}

export interface CompanyDetail {
  company: Company;
  careers_hiring_from_it: CareerSummary[];
}

// -- Sprint 3 — Project Knowledge Base (docs/AUREON_DATA_ARCHITECTURE.md §4) --

export interface Project {
  id: string;
  title: string;
  brief: string;
  difficulty_level: string;
  estimated_hours: number;
  target_skill_ids: string[];
  related_career_ids: string[];
  related_company_ids: string[];
  submission_type: string;
}

export interface ProjectsResponse {
  projects: Project[];
}

export interface ProjectDetail {
  project: Project;
  target_skills: Skill[];
  related_careers: CareerSummary[];
  related_companies: Company[];
}

/** Structured self-report, not a score — see backend's
 * ProjectAttemptEvidence. Structurally distinct from experiment
 * completion: a demonstrated artifact and/or a written account, not
 * emotional-state flags. */
export interface ProjectAttemptEvidenceRequest {
  artifact_url?: string | null;
  reflection?: string;
}

export interface ProjectAttempt {
  id: string;
  project_id: string;
  project_title: string;
  target_skill_ids: string[];
  attempted_at: string;
  evidence: {
    artifact_url: string | null;
    reflection: string;
  };
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

export interface InstitutionReview {
  role_label: string;
  quote: string;
  sentiment: "positive" | "mixed";
}

/** Profile dimensions, not rankings — each 1-5, computed fresh from real
 * counts, never a fabricated or persisted score. */
export interface InstitutionProfile {
  research: number;
  entrepreneurship: number;
  campus_life: number;
  international_exposure: number;
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
  // Explore Batch 1 — merged Entrance Hub content, no separate route.
  campus_life_and_culture: string;
  fees_summary: string;
  scholarships_summary: string;
  entrance_exams: EntranceExam[];
  // Explore Polish Batch additions.
  hostels: string[];
  exchange_programs: string[];
  campus_facilities: string[];
  student_reviews: InstitutionReview[];
  profile: InstitutionProfile | null;
}

export interface EntranceExam {
  id: string;
  name: string;
  description: string;
  eligibility: string[];
  preparation_guidance: string;
  typical_timeline: string;
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

export type DecisionMemoryActionType = "compared" | "shortlisted" | "removed" | "simulated";

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

// ---------------------------------------------------------------------------
// Explore Batch 1 — Global Trends, Exposure Universe, Opportunity Equality.
// Mirrors backend/src/aureon/shared/schemas.py's same-named DTOs.
// ---------------------------------------------------------------------------

export interface Trend {
  id: string;
  title: string;
  category: string;
  summary: string;
  description: string;
  affected_industries: string[];
  affected_skills: string[];
  regions: string[];
  time_horizon: string;
  source_note: string;
  // Explore Polish Batch additions.
  key_milestones: string[];
  countries_leading: string[];
  affected_careers: string[];
  research_papers: string[];
  companies: string[];
  startups: string[];
  government_initiatives: string[];
  risks: string[];
  opportunities: string[];
}

export interface TrendsResponse {
  trends: Trend[];
}

export interface FutureSkill {
  skill: string;
  mentioned_in_trend_count: number;
  related_trend_ids: string[];
}

export interface FutureSkillsResponse {
  skills: FutureSkill[];
}

export interface ExposureSuggestion {
  career: CareerSummary;
  curiosity_hook: string;
  // Explore Polish Batch additions — composed entirely from the
  // enriched Career catalog, plus one reused Experience Lab suggestion.
  mini_introduction: string;
  quick_project: string | null;
  watch: string[];
  read: string[];
  build: string[];
  join: string[];
  reflect_prompt: string;
  suggested_experience: ExperimentSummary | null;
  // Exposure Universe merge — set when this suggestion's industry
  // overlaps a currently-recommended Missing World; null when it doesn't.
  related_missing_world: string | null;
}

// --- Exposure Universe merge (Missing Worlds + Exposure Universe) -------

export interface WorldExposureSummary {
  world_name: string;
  level: WorldExplorationLevel;
}

export interface ExposureMap {
  engaged: WorldExposureSummary[];
  limited_or_none: WorldExposureSummary[];
}

export interface MissingWorldCard {
  world: CareerWorld;
  level: WorldExplorationLevel;
  match_count: number;
  why_missing: string;
  related_careers: CareerSummary[];
  linked_circle: KnowledgeCircleSummary | null;
}

export interface WorldRelatedStory {
  id: string;
  career_id: string;
  career_name: string;
  person_label: string;
  journey: string;
  advice: string;
}

export interface WorldExplorationDetail {
  world: CareerWorld;
  level: WorldExplorationLevel;
  match_count: number;
  why_missing: string;
  related_careers: CareerSummary[];
  related_stories: WorldRelatedStory[];
  related_experts: ExpertSummary[];
  linked_circle: KnowledgeCircleSummary | null;
}

export interface ExposureUniverseResponse {
  exposure_map: ExposureMap;
  missing_worlds: MissingWorldCard[];
  suggestions: ExposureSuggestion[];
}

export interface ExposureInteractionRequest {
  career_id: string;
  interaction: "opened" | "dismissed";
}

export interface OpportunitySummary {
  id: string;
  title: string;
  category: string;
  organization: string;
  description: string;
  location: string;
  is_remote: boolean;
  application_deadline: string | null;
  // Sprint 4 — null when no legitimate destination exists (illustrative
  // composite postings have nothing real to link to).
  official_link: string | null;
}

export interface OpportunityEqualityRecommendation {
  opportunity: OpportunitySummary;
  readiness_label: string;
  likelihood_of_self_discovery: "low" | "medium" | "high";
  why_shown: string;
  contributing_factors: string[];
}

export interface OpportunityEqualityResponse {
  recommendations: OpportunityEqualityRecommendation[];
}

export interface OpportunityEqualityInteractionRequest {
  opportunity_id: string;
  interaction: "viewed" | "saved";
}

// ---------------------------------------------------------------------------
// Discover Batch 2 — Career Experiments, Talent Discovery Lab. Mirrors
// backend/src/aureon/shared/schemas.py's same-named DTOs.
// ---------------------------------------------------------------------------

export type ExperimentCategory =
  | "read_abstract"
  | "debug_code"
  | "analyze_problem"
  | "observe_design"
  | "reflect_on_workflow";

export interface Experiment {
  id: string;
  title: string;
  category: ExperimentCategory;
  description: string;
  instructions: string;
  estimated_minutes: number;
  age_appropriate_note: string;
  related_world: string;
  target_traits: string[];
  related_life_mission_ids: string[];
  reflection_prompt: string;
  source_note: string;
}

export interface ExperimentsResponse {
  experiments: Experiment[];
  completed_experiment_ids: string[];
}

/** Structured self-report, not a score — each flag is a real reported
 * signal; absence is never treated as negative. */
export interface ExperimentEvidenceRequest {
  enjoyment: boolean;
  curiosity: boolean;
  frustration: boolean;
  persistence: boolean;
  confidence: boolean;
  reflection: string;
}

export interface ExperimentCompletion {
  id: string;
  experiment_id: string;
  experiment_title: string;
  related_world: string;
  completed_at: string;
  evidence: ExperimentEvidenceRequest;
}

export type TalentTier = "still_discovering" | "emerging" | "growing";

export interface TalentEvidenceItem {
  source: "career_dna" | "experiment" | "reflection";
  description: string;
  observed_at: string;
}

/** Never a numeric score, never claims certainty — `explanation` always
 * cites the real evidence behind it. */
export interface TalentPattern {
  talent: string;
  tier: TalentTier;
  explanation: string;
  evidence: TalentEvidenceItem[];
}

export interface TalentsResponse {
  patterns: TalentPattern[];
}

// ---------------------------------------------------------------------------
// Discover Navigation Refactor — Hidden Potential becomes the single
// canonical backend source for strengths/potential/evidence. GET /talents
// stays live as a deprecated compatibility endpoint; nothing in the UI
// calls it anymore. Mirrors backend/src/aureon/shared/schemas.py's
// HiddenPotentialResponse and friends.
// ---------------------------------------------------------------------------

/** A pure regrouping of each TalentPattern's own real `tier` — never a
 * new score. `emerging`/`growing`/`consistently_observed` are this
 * response's field names for the backend's still_discovering/emerging/
 * growing values. */
export interface StrengthsGroup {
  emerging: TalentPattern[];
  growing: TalentPattern[];
  consistently_observed: TalentPattern[];
}

export interface EvidenceTimelineItem {
  source: "career_dna" | "experiment" | "reflection";
  description: string;
  observed_at: string;
  talent: string;
}

export interface DiscoveryStatistics {
  traits_tracked: number;
  traits_with_strong_evidence: number;
  hidden_patterns_found: number;
  strengths_found: number;
  experiments_completed: number;
}

export interface HiddenPotentialResponse {
  hidden_patterns: HiddenPotentialPattern[];
  strengths: StrengthsGroup;
  /** Exactly one recommendation, reused verbatim from Progressive
   * Discovery — never a second, per-strength recommendation engine. */
  suggested_experience: ExperimentSummary | null;
  evidence_timeline: EvidenceTimelineItem[];
  discovery_statistics: DiscoveryStatistics;
}

// ---------------------------------------------------------------------------
// Discover Batch 4 — Missing Worlds. Mirrors
// backend/src/aureon/shared/schemas.py's same-named DTOs.
// ---------------------------------------------------------------------------

export interface CareerWorld {
  id: string;
  name: string;
  description: string;
  why_it_matters: string;
  global_importance: string;
  future_growth: string;
  famous_careers: string[];
  beginner_roadmap: string[];
  required_skills: string[];
  misconceptions: string[];
  related_industries: string[];
  videos: string[];
  books: string[];
  communities: string[];
  beginner_projects: string[];
  internships: string[];
  colleges: string[];
  companies: string[];
  source_note: string;
}

export type WorldExplorationLevel = "unexplored" | "partially_explored" | "explored";

export interface WorldExploration {
  world: CareerWorld;
  exploration_level: WorldExplorationLevel;
  match_count: number;
}

export interface MissingWorldsResponse {
  worlds: WorldExploration[];
  recommended_next: string[];
}

// ---------------------------------------------------------------------------
// Discover Batch 4 — Life Missions.
// ---------------------------------------------------------------------------

export interface LifeMission {
  id: string;
  name: string;
  description: string;
  famous_people: string[];
  organizations: string[];
  companies: string[];
  nonprofits: string[];
  books: string[];
  documentaries: string[];
  podcasts: string[];
  communities: string[];
  real_world_examples: string[];
  suggested_careers: string[];
  projects: string[];
  volunteering_opportunities: string[];
  research_areas: string[];
  startup_ideas: string[];
  source_note: string;
}

export type MissionTier = "still_emerging" | "growing" | "strong";
export type MissionTrend = "emerging" | "steady" | "fading" | "not_enough_evidence";

export interface MissionEvidenceItem {
  source: "career_dna" | "experiment" | "reflection" | "evidence_graph";
  description: string;
  observed_at: string;
}

export interface MissionResonance {
  mission: LifeMission;
  tier: MissionTier;
  trend: MissionTrend;
  explanation: string;
  evidence: MissionEvidenceItem[];
}

export interface LifeMissionsResponse {
  resonances: MissionResonance[];
  other_missions: LifeMission[];
}

// ---------------------------------------------------------------------------
// Experience Lab / Life Missions merge — Experience Lab is the single
// surviving Discover destination; Life Mission resonance surfaces inside
// it as "Your Emerging Missions" rather than as its own nav item.
// Mirrors backend/src/aureon/shared/schemas.py's EmergingMissionDTO /
// ExperienceLabViewResponse.
// ---------------------------------------------------------------------------

export interface EmergingMission {
  mission: LifeMission;
  tier: MissionTier;
  trend: MissionTrend;
  explanation: string;
  evidence: MissionEvidenceItem[];
  suggested_experience: Experiment | null;
}

export interface ExperienceLabViewResponse {
  recommended: Experiment[];
  mission_experiences: Experiment[];
  career_experiences: Experiment[];
  completed: ExperimentCompletion[];
  completed_experiment_ids: string[];
  emerging_missions: EmergingMission[];
}

// ---------------------------------------------------------------------------
// Discover Batch 5 — Learning Style Discovery. Mirrors
// backend/src/aureon/shared/schemas.py's same-named DTOs.
// ---------------------------------------------------------------------------

export interface LearningStyle {
  id: string;
  name: string;
  description: string;
  strengths: string[];
  excels_in: string[];
  common_struggles: string[];
  study_strategies: string[];
  note_taking_techniques: string[];
  memory_strategies: string[];
  active_learning_methods: string[];
  project_ideas: string[];
  practice_routines: string[];
  collaboration_techniques: string[];
  learning_environments: string[];
  productivity_systems: string[];
  recommended_books: string[];
  research_backed_resources: string[];
  online_courses: string[];
  communities: string[];
  ways_to_strengthen: string[];
  source_note: string;
}

export type LearningStyleTier = "still_emerging" | "growing" | "strong";

export interface LearningStyleEvidenceItem {
  source: "career_dna" | "experiment" | "reflection" | "evidence_graph" | "hidden_potential";
  description: string;
  observed_at: string;
}

/** A student can show several styles at once — none exclusive of
 * another, never a single locked-in result. */
export interface LearningStylePattern {
  style: LearningStyle;
  tier: LearningStyleTier;
  explanation: string;
  evidence: LearningStyleEvidenceItem[];
  recommended_experiments: Experiment[];
}

export interface LearningStylesResponse {
  patterns: LearningStylePattern[];
}

// ---------------------------------------------------------------------------
// Relevant Interests — a plain, evidence-grounded signal of real recurring
// student interest, used by Decision Lab's "Relevant Interests" strength
// card and its "Interest alignment" comparison dimension.
// ---------------------------------------------------------------------------

export interface InterestEvidenceItem {
  source: "world_signal" | "experiment" | "reflection" | "evidence_graph" | "life_missions" | "hidden_potential";
  description: string;
  observed_at: string;
}

/** `topic` is a real, dynamically-discovered string, never a fixed
 * catalog id. */
export interface RelevantInterest {
  topic: string;
  explanation: string;
  evidence: InterestEvidenceItem[];
}

// ---------------------------------------------------------------------------
// Connect Batch 1 — Expert Connect + Parent Connect. An expert IS a Mentor
// (see MentorSummary/MentorDetail above) — these are the additive Expert-
// named types layered on top, never a duplicate "Mentor" naming.
// ---------------------------------------------------------------------------

export interface LinkRef {
  label: string;
  url: string;
}

export type CareerJourneyStage =
  | "school"
  | "university"
  | "internship"
  | "first_job"
  | "career_transition"
  | "failure"
  | "turning_point"
  | "promotion"
  | "current_role";

export interface CareerJourneyMilestone {
  stage: CareerJourneyStage;
  label: string;
  description: string;
  year_label: string;
}

export interface ExpertSummary {
  id: string;
  name: string;
  profession: string;
  specialization: string;
  country: string;
  city: string;
  years_experience: number;
  industries: string[];
  organization: string;
  trait_tags: string[];
  who_should_talk_to_me: string[];
  photo_url: string | null;
  updated_at: string;
}

export interface ExpertDetail {
  id: string;
  name: string;
  role_type: string;
  profession: string;
  specialization: string;
  field: string;
  bio: string;
  country: string;
  city: string;
  industries: string[];
  education: string[];
  organization: string;
  current_role: string;
  years_experience: number;
  languages: string[];
  photo_url: string | null;
  who_should_talk_to_me: string[];
  trait_tags: string[];
  learning_style_fit: string;
  linked_careers: CareerSummary[];
  career_journey: CareerJourneyMilestone[];
  day_in_the_life: string;
  weekly_routine: string;
  biggest_challenges: string[];
  favourite_part: string;
  biggest_misconceptions: string[];
  what_surprised_them: string;
  biggest_mistake: string;
  one_regret: string;
  salary_reality: string;
  work_life_balance: string;
  advice_for_beginners: string;
  advice_for_parents: string;
  faqs: CareerFAQ[];
  projects: string[];
  research: string[];
  certifications: string[];
  conferences: string[];
  organizations: string[];
  volunteer_work: string[];
  portfolio_links: LinkRef[];
  social_links: LinkRef[];
  daily_skills: string[];
  daily_tools: string[];
  recommended_books: string[];
  recommended_communities: string[];
  suggested_books: string[];
  suggested_companies: string[];
  suggested_certifications: string[];
  available_slots: string[];
  upcoming_career_talks: CareerEvent[];
  updated_at: string;
  accepts_mentorship: boolean;
  max_students: number;
  current_mentee_count: number;
}

export interface ExpertSearchResponse {
  experts: ExpertSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface ExpertFiltersResponse {
  specializations: string[];
  industries: string[];
  countries: string[];
}

// --- Parent Connect ---

export interface ParentExpertAdvice {
  expert_id: string;
  expert_name: string;
  expert_profession: string;
  advice_for_parents: string;
  faqs: CareerFAQ[];
}

export interface ParentCareerView {
  career_id: string;
  career_name: string;
  one_liner: string;
  required_education: string;
  salary_ranges: SalaryRange[];
  demand_2030: string;
  demand_2035: string;
  demand_2040: string;
  common_misconceptions: string[];
  earning_reality: string;
  career_stability: string;
  work_life_balance: string;
  growth_opportunities: string;
  educational_pathways: string[];
  alternative_routes: string[];
  global_demand: string;
  risks: string[];
  opportunities: string[];
  expert_advice: ParentExpertAdvice[];
}

export type ParentQuestionCategory =
  | "salary"
  | "safety"
  | "stability"
  | "work_life_balance"
  | "growth"
  | "international"
  | "career_switching"
  | "other";

export interface ParentQuestion {
  id: string;
  category: ParentQuestionCategory;
  career_id: string | null;
  question: string;
  expert_response: string;
  responding_expert_id: string | null;
  is_seeded: boolean;
  created_at: string;
}

export interface ParentQuestionsResponse {
  questions: ParentQuestion[];
}

// --- Shared ("Joint") Session — UI always says "Joint Session" ---

export type SharedSessionStatus = "invited" | "scheduled" | "completed" | "cancelled";
export type SharedSessionAuthorRole = "student" | "participant" | "expert";

export interface SharedSessionNote {
  id: string;
  session_id: string;
  author_role: SharedSessionAuthorRole;
  note: string;
  created_at: string;
}

export interface SharedSession {
  id: string;
  student_id: string;
  mentor_id: string;
  career_id: string | null;
  access_token: string;
  participant_label: string;
  topic: string;
  status: SharedSessionStatus;
  scheduled_slot: string | null;
  created_at: string;
  updated_at: string;
}

export interface SharedSessionWithNotes extends SharedSession {
  notes: SharedSessionNote[];
}

export interface SharedSessionsResponse {
  sessions: SharedSession[];
}

// --- Journey Stories (Connect Batch 2) ---

export interface LinkedExpertRef {
  id: string;
  name: string;
  profession: string;
}

// Expert Connect / Journey Stories purpose split — "composite" and
// "publicly_documented" are professional/workplace narratives (Career
// Explorer's "Human Stories" only, never shown here). This standalone
// screen's real content is "composite_student_discovery"; "student_discovery"
// is reserved, unpopulated, for a future real student submission flow.
export type JourneyStoryType =
  | "composite"
  | "publicly_documented"
  | "composite_student_discovery"
  | "student_discovery";

export interface JourneyStory {
  id: string;
  career_id: string;
  career_name: string;
  person_label: string;
  background: string;
  journey: string;
  challenges: string;
  turning_points: string;
  advice: string;
  lessons_learned: string;
  trait_tags: string[];
  timeline: CareerJourneyMilestone[];
  career_switch: boolean;
  gap_year: boolean;
  uncertainty_period: string;
  current_outcome: string;
  industry: string;
  story_type: JourneyStoryType;
  source_reference: string;
  discovery_themes: string[];
  linked_expert: LinkedExpertRef | null;
  linked_life_mission_name: string | null;
}

export interface JourneyStorySearchResponse {
  stories: JourneyStory[];
  total: number;
  limit: number;
  offset: number;
}

export interface JourneyStoryFiltersResponse {
  industries: string[];
  careers: CareerSummary[];
  discovery_themes: string[];
}

export interface RelevantJourneyStoriesResponse {
  stories: JourneyStory[];
}

export interface ReflectOnJourneyStoryRequest {
  prompt: string;
  response: string;
}

export interface ReflectOnJourneyStoryResponse {
  recorded: boolean;
}

// --- Knowledge Circles (Connect Batch 2) ---

export interface KnowledgeCircleSummary {
  id: string;
  name: string;
  overview: string;
}

export interface KnowledgeCircleView {
  id: string;
  name: string;
  overview: string;
  what_this_field_is_about: string;
  beginner_roadmap: string[];
  beginner_projects: string[];
  advanced_projects: string[];
  laboratories: string[];
  startups: string[];
  ngos: string[];
  scholarships: string[];
  books: string[];
  documentaries: string[];
  podcasts: string[];
  youtube_channels: string[];
  journals_and_newsletters: string[];
  conferences: string[];
  competitions: string[];
  hackathons: string[];
  workshops: string[];
  communities: string[];
  open_source_projects: string[];
  research_organizations: string[];
  museums: string[];
  companies: string[];
  universities: string[];
  internships: string[];
  certifications: string[];
  research_papers: string[];
  government_initiatives: string[];
  volunteering_opportunities: string[];
}

export type CircleResourceStatus = "bookmarked" | "completed";

export interface CircleResourceProgress {
  id: string;
  circle_id: string;
  resource_type: string;
  resource_label: string;
  status: CircleResourceStatus;
  updated_at: string;
}

export interface CircleProgressResponse {
  progress: CircleResourceProgress[];
}

// --- Mentorship (Connect Batch 2) ---

export type MentorshipStatus = "requested" | "accepted" | "declined" | "completed";
export type MentorshipNoteAuthorRole = "student" | "expert";

export interface MentorshipProgressNote {
  id: string;
  author_role: MentorshipNoteAuthorRole;
  note: string;
  created_at: string;
}

export interface Mentorship {
  id: string;
  student_id: string;
  expert_id: string;
  review_token: string;
  status: MentorshipStatus;
  goals: string;
  progress_notes: MentorshipProgressNote[];
  created_at: string;
  updated_at: string;
  // Connect restructuring — resolved server-side from the real Mentor
  // record; empty strings when not resolvable.
  expert_name: string;
  expert_role: string;
  expert_domain: string;
}

export interface MentorshipsResponse {
  mentorships: Mentorship[];
}

// --- Decide Batch 1 — Decision Workspace ---
// Every nested type below (ExperimentCompletion, RelevantInterest,
// TalentPattern, LearningStylePattern, MissionResonance, CareerWorld,
// OpportunityEqualityRecommendation, ExpertSummary, JourneyStory,
// KnowledgeCircleSummary, SalaryRange) is reused verbatim from above —
// nothing here duplicates a shape that already exists.

export interface DecisionExplanation {
  supporting_by_source: Record<string, string[]>;
  contradicting_by_source: Record<string, string[]>;
  missing_evidence: string[];
  strength_traits: string[];
}

export interface ReadinessCheckpoints {
  has_reflection: boolean;
  has_experiment: boolean;
  has_expert_contact: boolean;
  has_explored_world: boolean;
  has_explored_opportunity: boolean;
  has_simulation: boolean;
  has_knowledge_circle_engagement: boolean;
  percent: number;
}

export interface RealityCheck {
  daily_work: string;
  work_life_balance: string;
  stress: string;
  automation_risk: string;
  remote_possibility: string;
  travel: string;
  industry_outlook: string;
  salary_ranges: SalaryRange[];
}

export type CardVerdict = "continue_exploring" | "ready_to_shortlist" | "hold_for_now";

export interface CardRecommendation {
  verdict: CardVerdict;
  reason: string;
}

export interface NextActionItem {
  label: string;
  href: string | null;
}

export interface CareerDecisionCard {
  // Overview
  career_id: string;
  career_name: string;
  one_liner: string;
  why_it_matters: string;
  confidence_label: string;
  confidence_band: string;
  demand_2030: string;
  demand_2035: string;
  demand_2040: string;
  readiness: ReadinessCheckpoints;
  // Reality Check
  reality_check: RealityCheck;
  // Evidence
  reasons_for: string[];
  reasons_against: string[];
  missing_evidence: string[];
  explanation: DecisionExplanation;
  // Strengths
  hidden_strengths: TalentPattern[];
  relevant_interests: RelevantInterest[];
  learning_style_pattern: LearningStylePattern | null;
  // Explore
  unexplored_worlds: CareerWorld[];
  related_life_missions: MissionResonance[];
  top_journey_stories: JourneyStory[];
  top_knowledge_circles: KnowledgeCircleSummary[];
  top_opportunities: OpportunityEqualityRecommendation[];
  // People
  top_experts: ExpertSummary[];
  // Your Next Step
  decision_gaps: string[];
  next_actions: NextActionItem[];
  recommendation: CardRecommendation;
}

export interface StageProgress {
  discover: boolean;
  explore: boolean;
  connect: boolean;
}

export interface DecisionWorkspaceResponse {
  cards: CareerDecisionCard[];
  workspace_gaps: string[];
  overall_readiness_percent: number;
  stage_progress: StageProgress;
}

// --- Suggest to Aureon ---------------------------------------------------

export type SuggestionCategory =
  | "career"
  | "opportunity"
  | "resource"
  | "feature_request"
  | "correction"
  | "general_feedback";

export type SuggestionStatus =
  | "pending"
  | "under_review"
  | "approved"
  | "rejected"
  | "implemented"
  | "needs_information";

export interface SuggestionRecord {
  id: string;
  student_id: string;
  category: SuggestionCategory;
  title: string;
  description: string;
  source_url: string | null;
  context_type: string | null;
  context_id: string | null;
  context_metadata: Record<string, unknown>;
  status: SuggestionStatus;
  review_notes: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SuggestionsResponse {
  suggestions: SuggestionRecord[];
}

export interface CreateSuggestionRequest {
  category: SuggestionCategory;
  title: string;
  description: string;
  source_url?: string | null;
  context_type?: string | null;
  context_id?: string | null;
  context_metadata?: Record<string, unknown> | null;
}
