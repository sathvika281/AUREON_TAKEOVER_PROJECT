import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { ProgressReport } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface ProgressContextValue {
  report: ProgressReport | null;
  isAnalyzing: boolean;
  error: string | null;
  analyzeProgress: () => Promise<void>;
}

const ProgressContext = createContext<ProgressContextValue | null>(null);

/**
 * Same shape as DecisionContext/CareerIntelligenceContext, but Progress
 * Intelligence's report is never persisted — there is nothing to fetch on
 * mount, only an on-demand analysis, same "conversation optional" button
 * pattern as every other analyze feature.
 */
export function ProgressProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [report, setReport] = useState<ProgressReport | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeProgress = useCallback(async () => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const response = await apiClient.post<ProgressReport>(
        `/v1/students/${studentId}/progress-report/analyze`,
        {},
      );
      setReport(response);
    } catch {
      setError("Aureon couldn't analyze your progress just now — please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  }, [studentId]);

  const value: ProgressContextValue = { report, isAnalyzing, error, analyzeProgress };

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>;
}

export function useProgressContext(): ProgressContextValue {
  const ctx = useContext(ProgressContext);
  if (!ctx) {
    throw new Error("useProgressContext must be used within a ProgressProvider");
  }
  return ctx;
}
