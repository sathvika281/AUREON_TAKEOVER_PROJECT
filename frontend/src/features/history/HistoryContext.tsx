import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CareerInvestigationRecord,
  CareerInvestigationsResponse,
  DocumentInvestigationRecord,
  DocumentInvestigationsResponse,
  GitHubInvestigationRecord,
  GitHubInvestigationsResponse,
  HistoryItem,
  HistoryResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface HistoryContextValue {
  items: HistoryItem[];
  githubInvestigations: GitHubInvestigationRecord[];
  documentInvestigations: DocumentInvestigationRecord[];
  searchInvestigations: CareerInvestigationRecord[];
  isLoading: boolean;
  /** Sprint 5 — Productization performance work. Only `/history` (used
   * by Mission Control) loads automatically at app mount. The 3
   * per-investigation-type collections below are only real content on
   * the Journey Timeline screen itself, so they're fetched lazily,
   * once, on first access to that screen via `ensureInvestigationsLoaded`. */
  isInvestigationsLoading: boolean;
  ensureInvestigationsLoaded: () => void;
}

const HistoryContext = createContext<HistoryContextValue | null>(null);

/** A pure read-aggregation over already-persisted investigations — never
 * regenerates anything. Fetched once on mount, same "conversation
 * optional" on-demand-elsewhere shape as every other feature context. */
export function HistoryProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [items, setItems] = useState<HistoryItem[]>([]);
  const [githubInvestigations, setGithubInvestigations] = useState<GitHubInvestigationRecord[]>([]);
  const [documentInvestigations, setDocumentInvestigations] = useState<DocumentInvestigationRecord[]>([]);
  const [searchInvestigations, setSearchInvestigations] = useState<CareerInvestigationRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isInvestigationsLoading, setIsInvestigationsLoading] = useState(false);
  const investigationsLoadedRef = useRef(false);

  useEffect(() => {
    apiClient
      .get<HistoryResponse>(`/v1/students/${studentId}/history`)
      .then((r) => setItems(r.items))
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [studentId]);

  const ensureInvestigationsLoaded = useCallback(() => {
    if (investigationsLoadedRef.current) return;
    investigationsLoadedRef.current = true;
    setIsInvestigationsLoading(true);
    Promise.all([
      apiClient
        .get<GitHubInvestigationsResponse>(`/v1/students/${studentId}/github-investigations`)
        .then((r) => setGithubInvestigations(r.investigations))
        .catch(() => {}),
      apiClient
        .get<DocumentInvestigationsResponse>(`/v1/students/${studentId}/document-investigations`)
        .then((r) => setDocumentInvestigations(r.investigations))
        .catch(() => {}),
      apiClient
        .get<CareerInvestigationsResponse>(`/v1/students/${studentId}/search-investigations`)
        .then((r) => setSearchInvestigations(r.investigations))
        .catch(() => {}),
    ]).finally(() => setIsInvestigationsLoading(false));
  }, [studentId]);

  const value: HistoryContextValue = {
    items, githubInvestigations, documentInvestigations, searchInvestigations, isLoading,
    isInvestigationsLoading, ensureInvestigationsLoaded,
  };

  return <HistoryContext.Provider value={value}>{children}</HistoryContext.Provider>;
}

export function useHistoryContext(): HistoryContextValue {
  const ctx = useContext(HistoryContext);
  if (!ctx) {
    throw new Error("useHistoryContext must be used within a HistoryProvider");
  }
  return ctx;
}
