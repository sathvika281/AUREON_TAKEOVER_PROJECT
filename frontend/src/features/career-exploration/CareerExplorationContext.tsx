import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CareerExplorationEvent,
  CareerExplorationHistoryResponse,
  CareerInteractionType,
  RecordCareerExplorationEventResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

const RECENTLY_EXPLORED_LIMIT = 5;

export interface RecentlyExploredEntry {
  careerId: string;
  careerName: string;
  lastInteractionType: CareerInteractionType;
  lastEventAt: string;
}

interface CareerExplorationContextValue {
  recentlyExplored: RecentlyExploredEntry[];
  isBookmarked: (careerId: string) => boolean;
  recordEvent: (
    careerId: string,
    interactionType: CareerInteractionType,
    metadata?: Record<string, unknown>,
  ) => Promise<void>;
}

const CareerExplorationContext = createContext<CareerExplorationContextValue | null>(null);

/**
 * Career Exploration History — observational only, never itself treated
 * as evidence (see backend domain/models/career_exploration.py). This
 * context is deliberately lightweight: it just persists interactions and
 * derives a "Recently Explored" list, with no inference about
 * preference or fit.
 */
export function CareerExplorationProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;
  const [events, setEvents] = useState<CareerExplorationEvent[]>([]);

  useEffect(() => {
    apiClient
      .get<CareerExplorationHistoryResponse>(`/v1/students/${studentId}/career-exploration-history`)
      .then((response) => setEvents(response.events))
      .catch(() => {
        // A brand-new student simply has no history yet — not an error.
      });
  }, [studentId]);

  const recordEvent = useCallback(
    async (
      careerId: string,
      interactionType: CareerInteractionType,
      metadata: Record<string, unknown> = {},
    ) => {
      try {
        const response = await apiClient.post<RecordCareerExplorationEventResponse>(
          `/v1/students/${studentId}/career-exploration-events`,
          { career_id: careerId, interaction_type: interactionType, metadata },
        );
        if (response.recorded) {
          setEvents((prev) => [
            {
              id: `${careerId}-${interactionType}-${Date.now()}`,
              career_id: careerId,
              interaction_type: interactionType,
              metadata,
              created_at: new Date().toISOString(),
            },
            ...prev,
          ]);
        }
      } catch {
        // Exploration logging is a lightweight, non-critical concern —
        // never surface an error to the student over this.
      }
    },
    [studentId],
  );

  const isBookmarked = useCallback(
    (careerId: string) => {
      const latest = events
        .filter((e) => e.career_id === careerId && (e.interaction_type === "bookmarked" || e.interaction_type === "removed"))
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
      return latest?.interaction_type === "bookmarked";
    },
    [events],
  );

  const recentlyExplored = useMemo<RecentlyExploredEntry[]>(() => {
    const byCareer = new Map<string, CareerExplorationEvent>();
    for (const event of events) {
      const existing = byCareer.get(event.career_id);
      if (!existing || new Date(event.created_at) > new Date(existing.created_at)) {
        byCareer.set(event.career_id, event);
      }
    }
    return Array.from(byCareer.values())
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, RECENTLY_EXPLORED_LIMIT)
      .map((e) => ({
        careerId: e.career_id,
        careerName: (e.metadata.career_name as string | undefined) ?? e.career_id,
        lastInteractionType: e.interaction_type,
        lastEventAt: e.created_at,
      }));
  }, [events]);

  const value: CareerExplorationContextValue = { recentlyExplored, isBookmarked, recordEvent };

  return <CareerExplorationContext.Provider value={value}>{children}</CareerExplorationContext.Provider>;
}

export function useCareerExplorationContext(): CareerExplorationContextValue {
  const ctx = useContext(CareerExplorationContext);
  if (!ctx) {
    throw new Error("useCareerExplorationContext must be used within a CareerExplorationProvider");
  }
  return ctx;
}
