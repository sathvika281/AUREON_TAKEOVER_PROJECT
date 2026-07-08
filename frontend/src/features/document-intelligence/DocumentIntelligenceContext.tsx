import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type { DocumentInvestigationResult } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface DocumentIntelligenceContextValue {
  result: DocumentInvestigationResult | null;
  isInvestigating: boolean;
  error: string | null;
  investigate: (file: File) => Promise<void>;
}

const DocumentIntelligenceContext = createContext<DocumentIntelligenceContextValue | null>(null);

/** Same on-demand mission shape as URL Intelligence (V6)/Progress
 * Intelligence — nothing persisted client-side, no fetch on mount. */
export function DocumentIntelligenceProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [result, setResult] = useState<DocumentInvestigationResult | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const investigate = useCallback(
    async (file: File) => {
      setIsInvestigating(true);
      setError(null);
      try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await apiClient.postForm<DocumentInvestigationResult>(
          `/v1/students/${studentId}/documents/analyze`,
          formData,
        );
        setResult(response);
      } catch {
        setError("Aureon couldn't investigate this document just now — please try again.");
      } finally {
        setIsInvestigating(false);
      }
    },
    [studentId],
  );

  const value: DocumentIntelligenceContextValue = { result, isInvestigating, error, investigate };

  return <DocumentIntelligenceContext.Provider value={value}>{children}</DocumentIntelligenceContext.Provider>;
}

export function useDocumentIntelligenceContext(): DocumentIntelligenceContextValue {
  const ctx = useContext(DocumentIntelligenceContext);
  if (!ctx) {
    throw new Error("useDocumentIntelligenceContext must be used within a DocumentIntelligenceProvider");
  }
  return ctx;
}
