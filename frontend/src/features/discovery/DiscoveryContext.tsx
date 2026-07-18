import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CareerHypothesis,
  ConversationTurnResponse,
  DiscoveryProfileResponse,
  EvidenceRecord,
  ExperimentSummary,
  HiddenPotentialPattern,
  NotebookEntry,
  OrbitStatus,
  PendingCheckIn,
  ProgressiveDiscoveryState,
  ReflectionEntry,
  SuggestedActivity,
  TraitSignal,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

export interface ChatMessage {
  role: "student" | "aureon";
  content: string;
}

const CONVERSATION_STORAGE_PREFIX = "aureon.conversation_id.";
const HYPOTHESIS_INSIGHT_SEEN_PREFIX = "aureon.seen_hypothesis_insight.";
const HIDDEN_POTENTIAL_INSIGHT_SEEN_PREFIX = "aureon.seen_hidden_potential_insight.";
const UNIVERSE_FORMED_SEEN_PREFIX = "aureon.seen_universe_formed.";

interface DiscoveryContextValue {
  messages: ChatMessage[];
  careerDna: Record<string, TraitSignal>;
  hypotheses: CareerHypothesis[];
  notebookEntries: NotebookEntry[];
  hiddenPotential: HiddenPotentialPattern[];
  evidenceGraph: EvidenceRecord[];
  reflectionJournal: ReflectionEntry[];
  reflectionPrompt: string | null;
  suggestedActivity: SuggestedActivity | null;
  confidenceScore: number;
  understandingStage: string;
  understandingNarrative: string;
  mode: string;
  isSending: boolean;
  error: string | null;
  insightMomentLine: string | null;
  dismissInsightMoment: () => void;
  sendMessage: (text: string) => Promise<void>;
  refreshProfile: () => Promise<void>;
  /** Discover Batch 1 backend migration — Orbit Status + the one
   * pending Curiosity Check-in, both real backend-computed state. */
  orbitStatus: OrbitStatus | null;
  pendingCuriosityCheckin: PendingCheckIn | null;
  answerCuriosityCheckIn: (world: string, chosenOptions: string[]) => Promise<void>;
  /** Discover Batch 2 — the single next real, uncompleted Career
   * Experiment to try, from the same Progressive Discovery response. */
  suggestedExperiment: ExperimentSummary | null;
}

const DiscoveryContext = createContext<DiscoveryContextValue | null>(null);

/**
 * All of this — Career DNA, hypotheses (with their evidence and lifecycle
 * status), the Discovery Notebook, and Hidden Potential — is now computed
 * and persisted server-side. This provider's job shrank to "render what
 * the API returns" rather than reconstructing history from diffs on
 * every page load, which is what used to make the Notebook not survive a
 * refresh or a new device.
 */
export function DiscoveryProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;
  const conversationStorageKey = `${CONVERSATION_STORAGE_PREFIX}${studentId}`;
  const hypothesisInsightSeenKey = `${HYPOTHESIS_INSIGHT_SEEN_PREFIX}${studentId}`;
  const hiddenPotentialInsightSeenKey = `${HIDDEN_POTENTIAL_INSIGHT_SEEN_PREFIX}${studentId}`;
  const universeFormedSeenKey = `${UNIVERSE_FORMED_SEEN_PREFIX}${studentId}`;

  const [conversationId, setConversationId] = useState<string | null>(() =>
    localStorage.getItem(conversationStorageKey),
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [careerDna, setCareerDna] = useState<Record<string, TraitSignal>>({});
  const [hypotheses, setHypotheses] = useState<CareerHypothesis[]>([]);
  const [notebookEntries, setNotebookEntries] = useState<NotebookEntry[]>([]);
  const [hiddenPotential, setHiddenPotential] = useState<HiddenPotentialPattern[]>([]);
  const [evidenceGraph, setEvidenceGraph] = useState<EvidenceRecord[]>([]);
  const [reflectionJournal, setReflectionJournal] = useState<ReflectionEntry[]>([]);
  const [reflectionPrompt, setReflectionPrompt] = useState<string | null>(null);
  const [suggestedActivity, setSuggestedActivity] = useState<SuggestedActivity | null>(null);
  const [confidenceScore, setConfidenceScore] = useState(0);
  const [understandingStage, setUnderstandingStage] = useState("Seed");
  const [understandingNarrative, setUnderstandingNarrative] = useState(
    "Nothing yet — every investigation plants a seed.",
  );
  const [mode, setMode] = useState("exploration");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [insightMomentLine, setInsightMomentLine] = useState<string | null>(null);
  const [orbitStatus, setOrbitStatus] = useState<OrbitStatus | null>(null);
  const [pendingCuriosityCheckin, setPendingCuriosityCheckin] = useState<PendingCheckIn | null>(null);
  const [suggestedExperiment, setSuggestedExperiment] = useState<ExperimentSummary | null>(null);

  // Only used to detect the 0->1 transitions that fire an Insight Moment
  // — a presentational, device-local concern, not data (the underlying
  // hypotheses/hidden-potential lists are already server-truth).
  const previousHypothesesCountRef = useRef(0);
  const previousHiddenPotentialCountRef = useRef(0);
  const previousUnderstandingStageRef = useRef("Seed");

  // Extracted so evidence added anywhere in the app (GitHub/Document/URL/
  // Search Intelligence, none of which know about this context) can pull
  // this same profile again on demand — otherwise the Universe's data
  // only ever reflects whatever existed at the one moment this provider
  // first mounted for the session.
  const refreshProfile = useCallback(async () => {
    try {
      const profile = await apiClient.get<DiscoveryProfileResponse>(
        `/v1/students/${studentId}/discovery-profile`,
      );
      setCareerDna(profile.career_dna);
      setHypotheses(profile.hypotheses);
      setNotebookEntries(profile.notebook_entries);
      setHiddenPotential(profile.hidden_potential);
      setEvidenceGraph(profile.evidence_graph);
      setReflectionJournal(profile.reflection_journal);
      setConfidenceScore(profile.confidence_score);
      setUnderstandingStage(profile.understanding_stage);
      setUnderstandingNarrative(profile.understanding_narrative);
      previousHypothesesCountRef.current = profile.hypotheses.length;
      previousHiddenPotentialCountRef.current = profile.hidden_potential.length;
      previousUnderstandingStageRef.current = profile.understanding_stage;
    } catch {
      // A brand-new student simply has no profile yet — not an error.
    }
  }, [studentId]);

  // Discover Batch 1 backend migration — Orbit Status + the one pending
  // Curiosity Check-in, both now real backend-computed state (Progressive
  // Discovery Service) rather than local lookup tables/Supabase metadata.
  const refreshProgressiveDiscovery = useCallback(async () => {
    try {
      const state = await apiClient.get<ProgressiveDiscoveryState>(
        `/v1/students/${studentId}/progressive-discovery`,
      );
      setOrbitStatus(state.orbit_status);
      setPendingCuriosityCheckin(state.pending_curiosity_checkin);
      setSuggestedExperiment(state.suggested_experiment);
    } catch {
      // A brand-new student simply has no profile yet — not an error.
    }
  }, [studentId]);

  const answerCuriosityCheckIn = useCallback(
    async (world: string, chosenOptions: string[]) => {
      const state = await apiClient.post<ProgressiveDiscoveryState>(
        `/v1/students/${studentId}/curiosity-checkins/answer`,
        { world, chosen_options: chosenOptions },
      );
      setOrbitStatus(state.orbit_status);
      setPendingCuriosityCheckin(state.pending_curiosity_checkin);
      setSuggestedExperiment(state.suggested_experiment);
    },
    [studentId],
  );

  useEffect(() => {
    void refreshProfile();
    void refreshProgressiveDiscovery();
    // Only ever re-run this for a genuinely different student — refreshProfile/
    // refreshProgressiveDiscovery are stable per studentId and callable on
    // demand after that.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studentId]);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isSending) return;

      const answeredPrompt = reflectionPrompt;
      setMessages((prev) => [...prev, { role: "student", content: trimmed }]);
      setIsSending(true);
      setError(null);

      try {
        const response = await apiClient.post<ConversationTurnResponse>(
          "/v1/conversation/turn",
          {
            student_id: studentId,
            conversation_id: conversationId,
            message: trimmed,
          },
        );

        if (response.conversation_id !== conversationId) {
          setConversationId(response.conversation_id);
          localStorage.setItem(conversationStorageKey, response.conversation_id);
        }

        setMessages((prev) => [...prev, { role: "aureon", content: response.reply }]);

        const hadNoHypotheses = previousHypothesesCountRef.current === 0;
        const hasHypothesesNow = response.hypotheses.length >= 1;
        const hadNoHiddenPotential = previousHiddenPotentialCountRef.current === 0;
        const hasHiddenPotentialNow = response.hidden_potential.length >= 1;
        const justReachedDecisionReady =
          previousUnderstandingStageRef.current !== "Decision Ready" &&
          response.understanding_stage === "Decision Ready";

        // At most one Insight Moment per turn — hypothesis formation
        // takes priority since it's the more significant milestone, then
        // Hidden Potential, then the universe-formed completion moment
        // (Decision Ready is the last of the two prior milestones, so it
        // can only ever fire after both have already had their chance).
        if (hadNoHypotheses && hasHypothesesNow && !localStorage.getItem(hypothesisInsightSeenKey)) {
          localStorage.setItem(hypothesisInsightSeenKey, "true");
          setInsightMomentLine("I think I'm beginning to understand you.");
        } else if (
          hadNoHiddenPotential &&
          hasHiddenPotentialNow &&
          !localStorage.getItem(hiddenPotentialInsightSeenKey)
        ) {
          localStorage.setItem(hiddenPotentialInsightSeenKey, "true");
          setInsightMomentLine(
            `Today Aureon found something unexpected. ${response.hidden_potential[0].sentence}`,
          );
        } else if (justReachedDecisionReady && !localStorage.getItem(universeFormedSeenKey)) {
          localStorage.setItem(universeFormedSeenKey, "true");
          setInsightMomentLine(
            "🌌 Your universe has become clearer. Every future conversation, project and investigation will continue refining it. Your journey has only begun.",
          );
        }
        previousHypothesesCountRef.current = response.hypotheses.length;
        previousHiddenPotentialCountRef.current = response.hidden_potential.length;
        previousUnderstandingStageRef.current = response.understanding_stage;

        setCareerDna(response.career_dna);
        setHypotheses(response.hypotheses);
        setNotebookEntries(response.notebook_entries);
        setHiddenPotential(response.hidden_potential);
        setSuggestedActivity(response.suggested_activity);
        setConfidenceScore(response.confidence_score);
        setUnderstandingStage(response.understanding_stage);
        setUnderstandingNarrative(response.understanding_narrative);
        setMode(response.mode);
        setReflectionPrompt(response.reflection_prompt);

        // The backend tracks a reflection being answered internally, but
        // doesn't echo the journal entry back on the turn response — the
        // full journal only comes from the profile-load endpoint, so this
        // is a small optimistic local append for immediate feedback.
        if (answeredPrompt) {
          const now = new Date().toISOString();
          setReflectionJournal((prev) => [
            ...prev,
            { prompt: answeredPrompt, response: trimmed, created_at: now, answered_at: now },
          ]);
        }

        // The turn response doesn't echo evidence_graph back (unlike career_dna/
        // hypotheses/notebook_entries) — refresh it so Your Universe's hover
        // explanations reflect evidence this very turn may have just added.
        void refreshProfile();
      } catch {
        setError("Aureon couldn't respond just now — please try again.");
      } finally {
        setIsSending(false);
      }
    },
    [
      conversationId,
      conversationStorageKey,
      hiddenPotentialInsightSeenKey,
      hypothesisInsightSeenKey,
      isSending,
      reflectionPrompt,
      refreshProfile,
      studentId,
    ],
  );

  const dismissInsightMoment = useCallback(() => setInsightMomentLine(null), []);

  const value: DiscoveryContextValue = {
    messages,
    careerDna,
    hypotheses,
    notebookEntries,
    hiddenPotential,
    evidenceGraph,
    reflectionJournal,
    reflectionPrompt,
    suggestedActivity,
    confidenceScore,
    understandingStage,
    understandingNarrative,
    mode,
    isSending,
    error,
    insightMomentLine,
    dismissInsightMoment,
    sendMessage,
    refreshProfile,
    orbitStatus,
    pendingCuriosityCheckin,
    answerCuriosityCheckIn,
    suggestedExperiment,
  };

  return <DiscoveryContext.Provider value={value}>{children}</DiscoveryContext.Provider>;
}

export function useDiscoveryContext(): DiscoveryContextValue {
  const ctx = useContext(DiscoveryContext);
  if (!ctx) {
    throw new Error("useDiscoveryContext must be used within a DiscoveryProvider");
  }
  return ctx;
}
