import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { UrlInvestigationResult } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface UrlInvestigationContextValue {
  result: UrlInvestigationResult | null;
  isInvestigating: boolean;
  error: string | null;
  investigate: (url: string) => Promise<void>;
}

const UrlInvestigationContext = createContext<UrlInvestigationContextValue | null>(null);

/** Same shape as every other analyze-on-demand context (Decision,
 * Progress) — an on-demand mission, nothing persisted client-side, no
 * fetch on mount. */
export function UrlInvestigationProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [result, setResult] = useState<UrlInvestigationResult | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const investigate = useCallback(
    async (url: string) => {
      setIsInvestigating(true);
      setError(null);
      try {
        const response = await apiClient.post<UrlInvestigationResult>(
          `/v1/students/${studentId}/url-investigations/analyze`,
          { url },
        );
        setResult(response);
      } catch {
        setError("Aureon couldn't investigate this URL just now — please try again.");
      } finally {
        setIsInvestigating(false);
      }
    },
    [studentId],
  );

  const value: UrlInvestigationContextValue = { result, isInvestigating, error, investigate };

  return <UrlInvestigationContext.Provider value={value}>{children}</UrlInvestigationContext.Provider>;
}

export function useUrlInvestigationContext(): UrlInvestigationContextValue {
  const ctx = useContext(UrlInvestigationContext);
  if (!ctx) {
    throw new Error("useUrlInvestigationContext must be used within a UrlInvestigationProvider");
  }
  return ctx;
}
