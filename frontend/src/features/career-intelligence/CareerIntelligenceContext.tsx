import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { CareerCandidate, CareerCandidatesResponse } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface CareerIntelligenceContextValue {
  candidates: CareerCandidate[];
  insufficientEvidence: boolean;
  insufficientEvidenceReason: string | null;
  isAnalyzing: boolean;
  error: string | null;
  hasAnalyzedOnce: boolean;
  recommendedColleges: string[];
  recommendedExperts: string[];
  analyzeCareers: () => Promise<void>;
  shortlistCandidate: (careerId: string) => Promise<void>;
  removeCandidate: (careerId: string) => Promise<void>;
  /** Sprint 5 — Productization performance work. Persisted candidates
   * used to fetch unconditionally at app mount; now lazy, once, on
   * first access via `ensureLoaded()` — call from Career Explorer,
   * Career Detail, and Decision Lab's own mount effects (all real
   * consumers). Idempotent across callers. */
  isLoadingInitialData: boolean;
  ensureLoaded: () => void;
}

const CareerIntelligenceContext = createContext<CareerIntelligenceContextValue | null>(null);

/**
 * Same shape as DiscoveryContext, but for a stateless, on-demand analysis
 * rather than a running conversation — "conversation optional" means this
 * is triggered by a button, not a chat message. Reads persisted candidates
 * on mount (survives refresh/new device), and re-runs analysis only when
 * the student explicitly asks.
 */
export function CareerIntelligenceProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [candidates, setCandidates] = useState<CareerCandidate[]>([]);
  const [insufficientEvidence, setInsufficientEvidence] = useState(false);
  const [insufficientEvidenceReason, setInsufficientEvidenceReason] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasAnalyzedOnce, setHasAnalyzedOnce] = useState(false);
  const [recommendedColleges, setRecommendedColleges] = useState<string[]>([]);
  const [recommendedExperts, setRecommendedExperts] = useState<string[]>([]);
  const [isLoadingInitialData, setIsLoadingInitialData] = useState(false);
  const hasLoadedRef = useRef(false);

  const ensureLoaded = useCallback(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    setIsLoadingInitialData(true);
    apiClient
      .get<CareerCandidatesResponse>(`/v1/students/${studentId}/career-candidates`)
      .then((response) => {
        setCandidates(response.candidates);
        setInsufficientEvidence(response.insufficient_evidence);
        setInsufficientEvidenceReason(response.insufficient_evidence_reason);
        setHasAnalyzedOnce(response.candidates.length > 0);
        setRecommendedColleges(response.recommended_colleges);
        setRecommendedExperts(response.recommended_experts);
      })
      .catch(() => {
        // A brand-new student simply has no candidates yet — not an error.
      })
      .finally(() => setIsLoadingInitialData(false));
  }, [studentId]);

  const analyzeCareers = useCallback(async () => {
    hasLoadedRef.current = true;
    setIsAnalyzing(true);
    setError(null);
    try {
      const response = await apiClient.post<CareerCandidatesResponse>(
        `/v1/students/${studentId}/career-candidates/analyze`,
        {},
      );
      setCandidates(response.candidates);
      setInsufficientEvidence(response.insufficient_evidence);
      setInsufficientEvidenceReason(response.insufficient_evidence_reason);
      setHasAnalyzedOnce(true);
      setRecommendedColleges(response.recommended_colleges);
      setRecommendedExperts(response.recommended_experts);
    } catch {
      setError("Aureon couldn't analyze careers just now — please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  }, [studentId]);

  const shortlistCandidate = useCallback(
    async (careerId: string) => {
      try {
        const response = await apiClient.post<CareerCandidatesResponse>(
          `/v1/students/${studentId}/career-candidates/${careerId}/shortlist`,
          {},
        );
        setCandidates(response.candidates);
      } catch {
        setError("Aureon couldn't shortlist this career just now — please try again.");
      }
    },
    [studentId],
  );

  const removeCandidate = useCallback(
    async (careerId: string) => {
      try {
        const response = await apiClient.post<CareerCandidatesResponse>(
          `/v1/students/${studentId}/career-candidates/${careerId}/remove`,
          {},
        );
        setCandidates(response.candidates);
      } catch {
        setError("Aureon couldn't remove this career just now — please try again.");
      }
    },
    [studentId],
  );

  const value: CareerIntelligenceContextValue = {
    candidates,
    insufficientEvidence,
    insufficientEvidenceReason,
    isAnalyzing,
    error,
    hasAnalyzedOnce,
    recommendedColleges,
    recommendedExperts,
    analyzeCareers,
    shortlistCandidate,
    removeCandidate,
    isLoadingInitialData,
    ensureLoaded,
  };

  return (
    <CareerIntelligenceContext.Provider value={value}>{children}</CareerIntelligenceContext.Provider>
  );
}

export function useCareerIntelligenceContext(): CareerIntelligenceContextValue {
  const ctx = useContext(CareerIntelligenceContext);
  if (!ctx) {
    throw new Error("useCareerIntelligenceContext must be used within a CareerIntelligenceProvider");
  }
  return ctx;
}
