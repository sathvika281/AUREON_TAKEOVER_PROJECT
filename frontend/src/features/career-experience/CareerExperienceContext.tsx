import { createContext, useCallback, useContext, useRef, useState } from "react";
import type { ReactNode } from "react";

import { apiClient } from "../../shared/api/client";
import type {
  CareerEvent,
  CareerEventsResponse,
  EventRegistrationRecord,
  EventRegistrationsResponse,
  ExpertSessionBooking,
  ExpertSessionBookingsResponse,
  GuidanceRequestRecord,
  GuidanceRequestsResponse,
  InstitutionSummary,
  Mentorship,
  MentorshipNoteAuthorRole,
  MentorshipsResponse,
  MentorSummary,
  SavedExpertsResponse,
  SharedSession,
  SharedSessionsResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface CareerExperienceContextValue {
  /** The real, full institution catalog — no longer partner-only. */
  institutions: InstitutionSummary[];
  experts: MentorSummary[];
  events: CareerEvent[];
  bookings: ExpertSessionBooking[];
  guidanceRequests: GuidanceRequestRecord[];
  registrations: EventRegistrationRecord[];
  savedExpertIds: string[];
  /** Connect Batch 1 — the student's own Joint (Shared) Session invites. */
  sharedSessions: SharedSession[];
  /** Connect Batch 2 — the student's own mentorship requests/relationships. */
  mentorships: Mentorship[];
  isBusy: boolean;
  error: string | null;
  /** Sprint 5 — Productization performance work. This feature area's own
   * 9 GET requests used to fire unconditionally at app mount (login),
   * regardless of whether the student ever visited Expert Connect/
   * College Explorer/My Mentors/Shared Sessions this session. Now
   * deferred: call `ensureLoaded()` once from each consuming screen's
   * own mount effect — idempotent (a ref guard means only the first
   * caller across all four screens actually fires the requests; later
   * callers/re-visits are no-ops). `isLoadingInitialData` is real
   * "these requests are in flight" state, distinct from an honestly
   * empty result — never conflate the two. */
  isLoadingInitialData: boolean;
  ensureLoaded: () => void;
  bookSession: (mentorId: string, slotStart: string, topic: string) => Promise<void>;
  requestGuidance: (mentorId: string, message: string) => Promise<void>;
  toggleSaveExpert: (mentorId: string) => Promise<void>;
  registerForEvent: (eventId: string) => Promise<void>;
  /** Returns the created session (its access_token is needed
   * immediately for the invite link) — unlike the other actions above,
   * this endpoint returns a single new record, not the full collection,
   * so the full list is refreshed locally alongside it. */
  createSharedSessionInvite: (mentorId: string, careerId: string | null, topic: string) => Promise<SharedSession | null>;
  /** Connect Batch 2 — same single-record-return shape as
   * `createSharedSessionInvite` above, for the same reason (the caller
   * needs the new mentorship's id/review_token immediately). */
  requestMentorship: (expertId: string, goals: string) => Promise<Mentorship | null>;
  addMentorshipNote: (mentorshipId: string, authorRole: MentorshipNoteAuthorRole, note: string) => Promise<void>;
  completeMentorship: (mentorshipId: string) => Promise<void>;
}

const CareerExperienceContext = createContext<CareerExperienceContextValue | null>(null);

/**
 * College Explorer + Expert Connect. Built entirely on top of the
 * existing Institution/Mentor Knowledge Bases — the full real
 * institution catalog, not just partner-flagged rows, plus richer
 * mentor fields; this context adds no new AI reasoning, only real
 * student-initiated actions (booking, guidance requests, saves, event
 * registration) persisted on the student's own profile.
 */
export function CareerExperienceProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [institutions, setInstitutions] = useState<InstitutionSummary[]>([]);
  const [experts, setExperts] = useState<MentorSummary[]>([]);
  const [events, setEvents] = useState<CareerEvent[]>([]);
  const [bookings, setBookings] = useState<ExpertSessionBooking[]>([]);
  const [guidanceRequests, setGuidanceRequests] = useState<GuidanceRequestRecord[]>([]);
  const [registrations, setRegistrations] = useState<EventRegistrationRecord[]>([]);
  const [savedExpertIds, setSavedExpertIds] = useState<string[]>([]);
  const [sharedSessions, setSharedSessions] = useState<SharedSession[]>([]);
  const [mentorships, setMentorships] = useState<Mentorship[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingInitialData, setIsLoadingInitialData] = useState(false);
  const hasLoadedRef = useRef(false);

  const ensureLoaded = useCallback(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    setIsLoadingInitialData(true);
    Promise.all([
      apiClient
        .get<InstitutionSummary[]>("/v1/institutions")
        .then(setInstitutions)
        .catch(() => {}),
      apiClient
        .get<MentorSummary[]>("/v1/mentors")
        .then(setExperts)
        .catch(() => {}),
      apiClient
        .get<CareerEventsResponse>("/v1/career-events")
        .then((r) => setEvents(r.events))
        .catch(() => {}),
      apiClient
        .get<ExpertSessionBookingsResponse>(`/v1/students/${studentId}/expert-sessions`)
        .then((r) => setBookings(r.bookings))
        .catch(() => {}),
      apiClient
        .get<GuidanceRequestsResponse>(`/v1/students/${studentId}/expert-guidance-requests`)
        .then((r) => setGuidanceRequests(r.requests))
        .catch(() => {}),
      apiClient
        .get<EventRegistrationsResponse>(`/v1/students/${studentId}/events/registrations`)
        .then((r) => setRegistrations(r.registrations))
        .catch(() => {}),
      apiClient
        .get<SavedExpertsResponse>(`/v1/students/${studentId}/saved-experts`)
        .then((r) => setSavedExpertIds(r.mentor_ids))
        .catch(() => {}),
      apiClient
        .get<SharedSessionsResponse>(`/v1/students/${studentId}/shared-sessions`)
        .then((r) => setSharedSessions(r.sessions))
        .catch(() => {}),
      apiClient
        .get<MentorshipsResponse>(`/v1/students/${studentId}/mentorships`)
        .then((r) => setMentorships(r.mentorships))
        .catch(() => {}),
    ]).finally(() => setIsLoadingInitialData(false));
  }, [studentId]);

  const bookSession = useCallback(
    async (mentorId: string, slotStart: string, topic: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const response = await apiClient.post<ExpertSessionBookingsResponse>(
          `/v1/students/${studentId}/expert-sessions/book`,
          { mentor_id: mentorId, slot_start: slotStart, topic },
        );
        setBookings(response.bookings);
      } catch {
        setError("Aureon couldn't book this session just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const requestGuidance = useCallback(
    async (mentorId: string, message: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const response = await apiClient.post<GuidanceRequestsResponse>(
          `/v1/students/${studentId}/expert-guidance-requests`,
          { mentor_id: mentorId, message },
        );
        setGuidanceRequests(response.requests);
      } catch {
        setError("Aureon couldn't send this guidance request just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const toggleSaveExpert = useCallback(
    async (mentorId: string) => {
      const isSaved = savedExpertIds.includes(mentorId);
      try {
        const response = isSaved
          ? await apiClient.delete<SavedExpertsResponse>(`/v1/students/${studentId}/saved-experts/${mentorId}`)
          : await apiClient.post<SavedExpertsResponse>(`/v1/students/${studentId}/saved-experts/${mentorId}`, {});
        setSavedExpertIds(response.mentor_ids);
      } catch {
        setError("Aureon couldn't update your saved experts just now — please try again.");
      }
    },
    [studentId, savedExpertIds],
  );

  const registerForEvent = useCallback(
    async (eventId: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const response = await apiClient.post<EventRegistrationsResponse>(
          `/v1/students/${studentId}/events/register`,
          { event_id: eventId },
        );
        setRegistrations(response.registrations);
      } catch {
        setError("Aureon couldn't register you for this event just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const createSharedSessionInvite = useCallback(
    async (mentorId: string, careerId: string | null, topic: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const session = await apiClient.post<SharedSession>(`/v1/students/${studentId}/shared-sessions`, {
          mentor_id: mentorId, career_id: careerId, topic,
        });
        setSharedSessions((prev) => [...prev, session]);
        return session;
      } catch {
        setError("Aureon couldn't create this joint session invite just now — please try again.");
        return null;
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const requestMentorship = useCallback(
    async (expertId: string, goals: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const mentorship = await apiClient.post<Mentorship>(`/v1/students/${studentId}/mentorships`, {
          expert_id: expertId, goals,
        });
        setMentorships((prev) => [...prev, mentorship]);
        return mentorship;
      } catch {
        setError("Aureon couldn't send this mentorship request just now — please try again.");
        return null;
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const addMentorshipNote = useCallback(
    async (mentorshipId: string, authorRole: MentorshipNoteAuthorRole, note: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const updated = await apiClient.post<Mentorship>(
          `/v1/students/${studentId}/mentorships/${mentorshipId}/notes`,
          { author_role: authorRole, note },
        );
        setMentorships((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      } catch {
        setError("Aureon couldn't add this note just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const completeMentorship = useCallback(
    async (mentorshipId: string) => {
      setIsBusy(true);
      setError(null);
      try {
        const updated = await apiClient.post<Mentorship>(
          `/v1/students/${studentId}/mentorships/${mentorshipId}/complete`,
          {},
        );
        setMentorships((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      } catch {
        setError("Aureon couldn't complete this mentorship just now — please try again.");
      } finally {
        setIsBusy(false);
      }
    },
    [studentId],
  );

  const value: CareerExperienceContextValue = {
    institutions,
    experts,
    events,
    bookings,
    guidanceRequests,
    registrations,
    savedExpertIds,
    sharedSessions,
    mentorships,
    isBusy,
    error,
    isLoadingInitialData,
    ensureLoaded,
    bookSession,
    requestGuidance,
    toggleSaveExpert,
    registerForEvent,
    createSharedSessionInvite,
    requestMentorship,
    addMentorshipNote,
    completeMentorship,
  };

  return <CareerExperienceContext.Provider value={value}>{children}</CareerExperienceContext.Provider>;
}

export function useCareerExperienceContext(): CareerExperienceContextValue {
  const ctx = useContext(CareerExperienceContext);
  if (!ctx) {
    throw new Error("useCareerExperienceContext must be used within a CareerExperienceProvider");
  }
  return ctx;
}
