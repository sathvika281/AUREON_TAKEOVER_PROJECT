import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CareerComparison,
  CareerComparisonsResponse,
  CareerDecisionCard,
  CareerSimulation,
  CareerSimulationsResponse,
  CollegeMatch,
  CollegeMatchesResponse,
  DecisionMemoryEntry,
  DecisionMemoryResponse,
  DecisionTimelineResponse,
  DecisionWorkspaceResponse,
  MentorMatch,
  MentorMatchesResponse,
  MissionSnapshot,
  StageProgress,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface DecisionContextValue {
  comparisons: CareerComparison[];
  mentorMatches: MentorMatch[];
  collegeMatches: CollegeMatch[];
  decisionMemory: DecisionMemoryEntry[];
  currentDirectionSummary: string;
  timelineMilestones: DecisionTimelineResponse["milestones"];
  isBusy: boolean;
  error: string | null;
  lastMentorMission: MissionSnapshot | null;
  lastMentorArtifactsUpdated: string[];
  lastCollegeMission: MissionSnapshot | null;
  lastCollegeArtifactsUpdated: string[];
  simulations: CareerSimulation[];
  simulationInsufficientReason: string | null;
  lastSimulationMission: MissionSnapshot | null;
  lastSimulationArtifactsUpdated: string[];
  recommendedColleges: string[];
  recommendedExperts: string[];
  /** Decide Batch 1 — the Decision Workspace: one composed card per
   * active career candidate, plus workspace-level aggregates. */
  workspace: CareerDecisionCard[];
  workspaceGaps: string[];
  overallReadinessPercent: number;
  stageProgress: StageProgress;
  runComparison: (careerIds: string[]) => Promise<void>;
  analyzeMentors: () => Promise<void>;
  analyzeColleges: () => Promise<void>;
  runSimulation: (careerIds: string[]) => Promise<void>;
  refreshTimelineAndMemory: () => Promise<void>;
  refreshWorkspace: () => Promise<void>;
  /** Sprint 5 — Productization performance work. Only `decisionMemory`
   * loads automatically at app mount (Mission Control needs it). Every
   * other field here — comparisons, mentor/college matches,
   * simulations, timeline, workspace — used to fire unconditionally
   * alongside it, even for a student who never opens Decision Lab this
   * session. Each is now fetched lazily, once, on first access via
   * these guarded callbacks — call the relevant one from a consuming
   * screen's own mount effect. Idempotent: safe to call from more than
   * one screen (e.g. Decision Lab and History both need comparisons). */
  ensureComparisonsLoaded: () => void;
  ensureMentorMatchesLoaded: () => void;
  ensureCollegeMatchesLoaded: () => void;
  ensureSimulationsLoaded: () => void;
  ensureTimelineLoaded: () => void;
  ensureWorkspaceLoaded: () => void;
  isComparisonsLoading: boolean;
  isMentorMatchesLoading: boolean;
  isCollegeMatchesLoading: boolean;
  isSimulationsLoading: boolean;
  isTimelineLoading: boolean;
  isWorkspaceLoading: boolean;
}

const DecisionContext = createContext<DecisionContextValue | null>(null);

/**
 * Same shape as CareerIntelligenceContext — fetches Phase 3's persisted
 * data on mount, exposes on-demand actions ("conversation optional").
 */
export function DecisionProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [comparisons, setComparisons] = useState<CareerComparison[]>([]);
  const [mentorMatches, setMentorMatches] = useState<MentorMatch[]>([]);
  const [collegeMatches, setCollegeMatches] = useState<CollegeMatch[]>([]);
  const [decisionMemory, setDecisionMemory] = useState<DecisionMemoryEntry[]>([]);
  const [currentDirectionSummary, setCurrentDirectionSummary] = useState("No clear direction yet.");
  const [timelineMilestones, setTimelineMilestones] = useState<DecisionTimelineResponse["milestones"]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMentorMission, setLastMentorMission] = useState<MissionSnapshot | null>(null);
  const [lastMentorArtifactsUpdated, setLastMentorArtifactsUpdated] = useState<string[]>([]);
  const [lastCollegeMission, setLastCollegeMission] = useState<MissionSnapshot | null>(null);
  const [lastCollegeArtifactsUpdated, setLastCollegeArtifactsUpdated] = useState<string[]>([]);
  const [simulations, setSimulations] = useState<CareerSimulation[]>([]);
  const [simulationInsufficientReason, setSimulationInsufficientReason] = useState<string | null>(null);
  const [lastSimulationMission, setLastSimulationMission] = useState<MissionSnapshot | null>(null);
  const [lastSimulationArtifactsUpdated, setLastSimulationArtifactsUpdated] = useState<string[]>([]);
  const [recommendedColleges, setRecommendedColleges] = useState<string[]>([]);
  const [recommendedExperts, setRecommendedExperts] = useState<string[]>([]);
  const [workspace, setWorkspace] = useState<CareerDecisionCard[]>([]);
  const [workspaceGaps, setWorkspaceGaps] = useState<string[]>([]);
  const [overallReadinessPercent, setOverallReadinessPercent] = useState(0);
  const [stageProgress, setStageProgress] = useState<StageProgress>({ discover: false, explore: false, connect: false });
  const [isComparisonsLoading, setIsComparisonsLoading] = useState(false);
  const [isMentorMatchesLoading, setIsMentorMatchesLoading] = useState(false);
  const [isCollegeMatchesLoading, setIsCollegeMatchesLoading] = useState(false);
  const [isSimulationsLoading, setIsSimulationsLoading] = useState(false);
  const [isTimelineLoading, setIsTimelineLoading] = useState(false);
  const [isWorkspaceLoading, setIsWorkspaceLoading] = useState(false);

  const comparisonsLoadedRef = useRef(false);
  const mentorMatchesLoadedRef = useRef(false);
  const collegeMatchesLoadedRef = useRef(false);
  const simulationsLoadedRef = useRef(false);
  const timelineLoadedRef = useRef(false);
  const workspaceLoadedRef = useRef(false);

  const refreshWorkspace = useCallback(async () => {
    workspaceLoadedRef.current = true;
    try {
      const response = await apiClient.get<DecisionWorkspaceResponse>(`/v1/students/${studentId}/decision-workspace`);
      setWorkspace(response.cards);
      setWorkspaceGaps(response.workspace_gaps);
      setOverallReadinessPercent(response.overall_readiness_percent);
      setStageProgress(response.stage_progress);
    } catch {
      // No candidates yet for a brand-new student — not an error.
    }
  }, [studentId]);

  const ensureWorkspaceLoaded = useCallback(() => {
    if (workspaceLoadedRef.current) return;
    setIsWorkspaceLoading(true);
    void refreshWorkspace().finally(() => setIsWorkspaceLoading(false));
  }, [refreshWorkspace]);

  const refreshTimelineAndMemory = useCallback(async () => {
    timelineLoadedRef.current = true;
    try {
      const [timeline, memory] = await Promise.all([
        apiClient.get<DecisionTimelineResponse>(`/v1/students/${studentId}/decision-timeline`),
        apiClient.get<DecisionMemoryResponse>(`/v1/students/${studentId}/decision-memory`),
      ]);
      setTimelineMilestones(timeline.milestones);
      setCurrentDirectionSummary(timeline.current_direction_summary);
      setDecisionMemory(memory.entries);
    } catch {
      // No data yet for a brand-new student — not an error.
    }
  }, [studentId]);

  const ensureTimelineLoaded = useCallback(() => {
    if (timelineLoadedRef.current) return;
    timelineLoadedRef.current = true;
    setIsTimelineLoading(true);
    apiClient
      .get<DecisionTimelineResponse>(`/v1/students/${studentId}/decision-timeline`)
      .then((timeline) => {
        setTimelineMilestones(timeline.milestones);
        setCurrentDirectionSummary(timeline.current_direction_summary);
      })
      .catch(() => {})
      .finally(() => setIsTimelineLoading(false));
  }, [studentId]);

  const ensureComparisonsLoaded = useCallback(() => {
    if (comparisonsLoadedRef.current) return;
    comparisonsLoadedRef.current = true;
    setIsComparisonsLoading(true);
    apiClient
      .get<CareerComparisonsResponse>(`/v1/students/${studentId}/career-comparisons`)
      .then((r) => {
        setComparisons(r.comparisons);
        setRecommendedColleges(r.recommended_colleges);
        setRecommendedExperts(r.recommended_experts);
      })
      .catch(() => {})
      .finally(() => setIsComparisonsLoading(false));
  }, [studentId]);

  const ensureMentorMatchesLoaded = useCallback(() => {
    if (mentorMatchesLoadedRef.current) return;
    mentorMatchesLoadedRef.current = true;
    setIsMentorMatchesLoading(true);
    apiClient
      .get<MentorMatchesResponse>(`/v1/students/${studentId}/mentor-matches`)
      .then((r) => setMentorMatches(r.matches))
      .catch(() => {})
      .finally(() => setIsMentorMatchesLoading(false));
  }, [studentId]);

  const ensureCollegeMatchesLoaded = useCallback(() => {
    if (collegeMatchesLoadedRef.current) return;
    collegeMatchesLoadedRef.current = true;
    setIsCollegeMatchesLoading(true);
    apiClient
      .get<CollegeMatchesResponse>(`/v1/students/${studentId}/college-matches`)
      .then((r) => setCollegeMatches(r.matches))
      .catch(() => {})
      .finally(() => setIsCollegeMatchesLoading(false));
  }, [studentId]);

  const ensureSimulationsLoaded = useCallback(() => {
    if (simulationsLoadedRef.current) return;
    simulationsLoadedRef.current = true;
    setIsSimulationsLoading(true);
    apiClient
      .get<CareerSimulationsResponse>(`/v1/students/${studentId}/career-simulations`)
      .then((r) => setSimulations(r.simulations))
      .catch(() => {})
      .finally(() => setIsSimulationsLoading(false));
  }, [studentId]);

  useEffect(() => {
    apiClient
      .get<DecisionMemoryResponse>(`/v1/students/${studentId}/decision-memory`)
      .then((r) => setDecisionMemory(r.entries))
      .catch(() => {});
  }, [studentId]);

  const runComparison = useCallback(
    async (careerIds: string[]) => {
      setIsBusy(true);
      setError(null);
      try {
        comparisonsLoadedRef.current = true;
        const response = await apiClient.post<CareerComparisonsResponse>(
          `/v1/students/${studentId}/career-comparisons`,
          { career_ids: careerIds },
        );
        setComparisons(response.comparisons);
        setRecommendedColleges(response.recommended_colleges);
        setRecommendedExperts(response.recommended_experts);
        await refreshTimelineAndMemory();
        await refreshWorkspace();
      } catch {
        setError("Aureon couldn't compare these careers just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId, refreshTimelineAndMemory, refreshWorkspace],
  );

  const analyzeMentors = useCallback(async () => {
    setIsBusy(true);
    setError(null);
    try {
      mentorMatchesLoadedRef.current = true;
      const response = await apiClient.post<MentorMatchesResponse>(
        `/v1/students/${studentId}/mentor-matches/analyze`,
        {},
      );
      setMentorMatches(response.matches);
      setLastMentorMission(response.mission);
      setLastMentorArtifactsUpdated(response.artifacts_updated);
    } catch {
      setError("Aureon couldn't match mentors just now — please try again.");
    } finally {
      setIsBusy(false);
    }
  }, [studentId]);

  const analyzeColleges = useCallback(async () => {
    setIsBusy(true);
    setError(null);
    try {
      collegeMatchesLoadedRef.current = true;
      const response = await apiClient.post<CollegeMatchesResponse>(
        `/v1/students/${studentId}/college-matches/analyze`,
        {},
      );
      setCollegeMatches(response.matches);
      setLastCollegeMission(response.mission);
      setLastCollegeArtifactsUpdated(response.artifacts_updated);
    } catch {
      setError("Aureon couldn't match institutions just now — please try again.");
    } finally {
      setIsBusy(false);
    }
  }, [studentId]);

  const runSimulation = useCallback(
    async (careerIds: string[]) => {
      setIsBusy(true);
      setError(null);
      try {
        simulationsLoadedRef.current = true;
        const response = await apiClient.post<CareerSimulationsResponse>(
          `/v1/students/${studentId}/career-simulations/analyze`,
          { career_ids: careerIds },
        );
        setSimulations(response.simulations);
        setSimulationInsufficientReason(response.insufficient_evidence ? response.insufficient_evidence_reason : null);
        setLastSimulationMission(response.mission);
        setLastSimulationArtifactsUpdated(response.artifacts_updated);
        await refreshTimelineAndMemory();
        await refreshWorkspace();
      } catch {
        setError("Aureon couldn't simulate these career paths just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId, refreshTimelineAndMemory, refreshWorkspace],
  );

  const value: DecisionContextValue = {
    comparisons,
    mentorMatches,
    collegeMatches,
    decisionMemory,
    currentDirectionSummary,
    timelineMilestones,
    isBusy,
    error,
    lastMentorMission,
    lastMentorArtifactsUpdated,
    lastCollegeMission,
    lastCollegeArtifactsUpdated,
    simulations,
    simulationInsufficientReason,
    lastSimulationMission,
    lastSimulationArtifactsUpdated,
    recommendedColleges,
    recommendedExperts,
    workspace,
    workspaceGaps,
    overallReadinessPercent,
    stageProgress,
    runComparison,
    analyzeMentors,
    analyzeColleges,
    runSimulation,
    refreshTimelineAndMemory,
    refreshWorkspace,
    ensureComparisonsLoaded,
    ensureMentorMatchesLoaded,
    ensureCollegeMatchesLoaded,
    ensureSimulationsLoaded,
    ensureTimelineLoaded,
    ensureWorkspaceLoaded,
    isComparisonsLoading,
    isMentorMatchesLoading,
    isCollegeMatchesLoading,
    isSimulationsLoading,
    isTimelineLoading,
    isWorkspaceLoading,
  };

  return <DecisionContext.Provider value={value}>{children}</DecisionContext.Provider>;
}

export function useDecisionContext(): DecisionContextValue {
  const ctx = useContext(DecisionContext);
  if (!ctx) {
    throw new Error("useDecisionContext must be used within a DecisionProvider");
  }
  return ctx;
}
