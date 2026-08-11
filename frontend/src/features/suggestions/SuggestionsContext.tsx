import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CreateSuggestionRequest,
  SuggestionCategory,
  SuggestionRecord,
  SuggestionsResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

/** What the modal opens pre-seeded with — set by a context-aware trigger
 * (e.g. "Suggest a correction" on a career detail screen) or left empty
 * for the generic global entry point. */
export interface SuggestionModalPrefill {
  category?: SuggestionCategory;
  context_type?: string;
  context_id?: string;
  context_metadata?: Record<string, unknown>;
}

interface SuggestionsContextValue {
  suggestions: SuggestionRecord[];
  isModalOpen: boolean;
  modalPrefill: SuggestionModalPrefill | null;
  openModal: (prefill?: SuggestionModalPrefill) => void;
  closeModal: () => void;
  isBusy: boolean;
  error: string | null;
  submitSuggestion: (request: CreateSuggestionRequest) => Promise<SuggestionRecord | null>;
  /** Sprint 5 — Productization performance work. The nav only ever
   * needs `openModal` — it used to sit behind this provider's own
   * unconditional mount-time fetch of the full suggestion list, which
   * every navigation click paid for even though it never reads
   * `suggestions`. Now lazy: `MySuggestionsScreen` (the only real
   * consumer of the list) calls `ensureLoaded()` on its own mount. */
  isLoadingInitialData: boolean;
  ensureLoaded: () => void;
}

const SuggestionsContext = createContext<SuggestionsContextValue | null>(null);

/**
 * "Help Aureon Grow" — a lightweight, globally-accessible contribution
 * feature (career/opportunity/resource suggestions, feature requests,
 * corrections, general feedback), deliberately not a fifth journey stage.
 * Every submission starts `pending` and is reviewed by a human before it
 * ever influences trusted data — this context only ever creates and
 * lists the student's own suggestions, never changes their status.
 */
export function SuggestionsProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [suggestions, setSuggestions] = useState<SuggestionRecord[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalPrefill, setModalPrefill] = useState<SuggestionModalPrefill | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingInitialData, setIsLoadingInitialData] = useState(false);
  const hasLoadedRef = useRef(false);

  const ensureLoaded = useCallback(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    setIsLoadingInitialData(true);
    apiClient
      .get<SuggestionsResponse>(`/v1/students/${studentId}/suggestions`)
      .then((r) => setSuggestions(r.suggestions))
      .catch(() => {})
      .finally(() => setIsLoadingInitialData(false));
  }, [studentId]);

  const openModal = useCallback((prefill?: SuggestionModalPrefill) => {
    setModalPrefill(prefill ?? null);
    setError(null);
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setModalPrefill(null);
  }, []);

  const submitSuggestion = useCallback(
    async (request: CreateSuggestionRequest) => {
      setIsBusy(true);
      setError(null);
      try {
        const created = await apiClient.post<SuggestionRecord>(
          `/v1/students/${studentId}/suggestions`,
          request,
        );
        setSuggestions((prev) => [created, ...prev]);
        return created;
      } catch {
        setError("Aureon couldn't send this just now — please try again.");
        return null;
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const value: SuggestionsContextValue = {
    suggestions,
    isModalOpen,
    modalPrefill,
    openModal,
    closeModal,
    isBusy,
    error,
    submitSuggestion,
    isLoadingInitialData,
    ensureLoaded,
  };

  return <SuggestionsContext.Provider value={value}>{children}</SuggestionsContext.Provider>;
}

export function useSuggestionsContext(): SuggestionsContextValue {
  const ctx = useContext(SuggestionsContext);
  if (!ctx) {
    throw new Error("useSuggestionsContext must be used within a SuggestionsProvider");
  }
  return ctx;
}
