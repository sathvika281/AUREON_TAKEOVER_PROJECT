import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
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
  MentorSummary,
  SavedExpertsResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

interface CareerExperienceContextValue {
  partnerColleges: InstitutionSummary[];
  experts: MentorSummary[];
  events: CareerEvent[];
  bookings: ExpertSessionBooking[];
  guidanceRequests: GuidanceRequestRecord[];
  registrations: EventRegistrationRecord[];
  savedExpertIds: string[];
  isBusy: boolean;
  error: string | null;
  bookSession: (mentorId: string, slotStart: string, topic: string) => Promise<void>;
  requestGuidance: (mentorId: string, message: string) => Promise<void>;
  toggleSaveExpert: (mentorId: string) => Promise<void>;
  registerForEvent: (eventId: string) => Promise<void>;
}

const CareerExperienceContext = createContext<CareerExperienceContextValue | null>(null);

/**
 * Career Exploration Ecosystem — College Collaboration + Expert Connect.
 * Built entirely on top of the existing Institution/Mentor Knowledge
 * Bases (partner-flagged institutions, richer mentor fields); this
 * context adds no new AI reasoning, only real student-initiated actions
 * (booking, guidance requests, saves, event registration) persisted on
 * the student's own profile.
 */
export function CareerExperienceProvider({ children }: { children: ReactNode }) {
  const studentId = useRef(getCurrentStudentId()).current;

  const [partnerColleges, setPartnerColleges] = useState<InstitutionSummary[]>([]);
  const [experts, setExperts] = useState<MentorSummary[]>([]);
  const [events, setEvents] = useState<CareerEvent[]>([]);
  const [bookings, setBookings] = useState<ExpertSessionBooking[]>([]);
  const [guidanceRequests, setGuidanceRequests] = useState<GuidanceRequestRecord[]>([]);
  const [registrations, setRegistrations] = useState<EventRegistrationRecord[]>([]);
  const [savedExpertIds, setSavedExpertIds] = useState<string[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<InstitutionSummary[]>("/v1/institutions?is_partner=true")
      .then(setPartnerColleges)
      .catch(() => {});
    apiClient
      .get<MentorSummary[]>("/v1/mentors")
      .then(setExperts)
      .catch(() => {});
    apiClient
      .get<CareerEventsResponse>("/v1/career-events")
      .then((r) => setEvents(r.events))
      .catch(() => {});
    apiClient
      .get<ExpertSessionBookingsResponse>(`/v1/students/${studentId}/expert-sessions`)
      .then((r) => setBookings(r.bookings))
      .catch(() => {});
    apiClient
      .get<GuidanceRequestsResponse>(`/v1/students/${studentId}/expert-guidance-requests`)
      .then((r) => setGuidanceRequests(r.requests))
      .catch(() => {});
    apiClient
      .get<EventRegistrationsResponse>(`/v1/students/${studentId}/events/registrations`)
      .then((r) => setRegistrations(r.registrations))
      .catch(() => {});
    apiClient
      .get<SavedExpertsResponse>(`/v1/students/${studentId}/saved-experts`)
      .then((r) => setSavedExpertIds(r.mentor_ids))
      .catch(() => {});
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

  const value: CareerExperienceContextValue = {
    partnerColleges,
    experts,
    events,
    bookings,
    guidanceRequests,
    registrations,
    savedExpertIds,
    isBusy,
    error,
    bookSession,
    requestGuidance,
    toggleSaveExpert,
    registerForEvent,
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
