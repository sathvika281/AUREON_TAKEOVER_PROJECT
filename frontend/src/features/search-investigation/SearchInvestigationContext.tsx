import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { SearchInvestigationResult } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface SearchInvestigationContextValue {
  result: SearchInvestigationResult | null;
  isInvestigating: boolean;
  error: string | null;
  investigate: (question: string) => Promise<void>;
}

const SearchInvestigationContext = createContext<SearchInvestigationContextValue | null>(null);

/** Same on-demand mission shape as URL/Document/GitHub Intelligence —
 * nothing persisted client-side, no fetch on mount. */
export function SearchInvestigationProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [result, setResult] = useState<SearchInvestigationResult | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const investigate = useCallback(
    async (question: string) => {
      setIsInvestigating(true);
      setError(null);
      try {
        const response = await apiClient.post<SearchInvestigationResult>(
          `/v1/students/${studentId}/search-investigations/analyze`,
          { question },
        );
        setResult(response);
      } catch {
        setError("Aureon couldn't complete this investigation just now — please try again.");
      } finally {
        setIsInvestigating(false);
      }
    },
    [studentId],
  );

  const value: SearchInvestigationContextValue = { result, isInvestigating, error, investigate };

  return <SearchInvestigationContext.Provider value={value}>{children}</SearchInvestigationContext.Provider>;
}

export function useSearchInvestigationContext(): SearchInvestigationContextValue {
  const ctx = useContext(SearchInvestigationContext);
  if (!ctx) {
    throw new Error("useSearchInvestigationContext must be used within a SearchInvestigationProvider");
  }
  return ctx;
}
