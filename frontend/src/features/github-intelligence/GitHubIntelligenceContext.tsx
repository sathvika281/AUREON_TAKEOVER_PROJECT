import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { GitHubInvestigationResult } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface GitHubIntelligenceContextValue {
  result: GitHubInvestigationResult | null;
  isInvestigating: boolean;
  error: string | null;
  investigate: (url: string) => Promise<void>;
}

const GitHubIntelligenceContext = createContext<GitHubIntelligenceContextValue | null>(null);

/** Same on-demand mission shape as URL/Document Intelligence — nothing
 * persisted client-side, no fetch on mount. */
export function GitHubIntelligenceProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [result, setResult] = useState<GitHubInvestigationResult | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const investigate = useCallback(
    async (url: string) => {
      setIsInvestigating(true);
      setError(null);
      try {
        const response = await apiClient.post<GitHubInvestigationResult>(
          `/v1/students/${studentId}/github/analyze`,
          { url },
        );
        setResult(response);
      } catch {
        setError("Aureon couldn't investigate this repository just now — please try again.");
      } finally {
        setIsInvestigating(false);
      }
    },
    [studentId],
  );

  const value: GitHubIntelligenceContextValue = { result, isInvestigating, error, investigate };

  return <GitHubIntelligenceContext.Provider value={value}>{children}</GitHubIntelligenceContext.Provider>;
}

export function useGitHubIntelligenceContext(): GitHubIntelligenceContextValue {
  const ctx = useContext(GitHubIntelligenceContext);
  if (!ctx) {
    throw new Error("useGitHubIntelligenceContext must be used within a GitHubIntelligenceProvider");
  }
  return ctx;
}
