import { useEffect, useState } from "react";
import { CalendarDays, Heart, Users } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import { apiClient } from "../../shared/api/client";
import type { MentorDetail, MentorSummary } from "../../shared/api/types";
import { useCareerExperienceContext } from "./CareerExperienceContext";

/**
 * Expert Connect — browse Aureon's real mentor pool (richer bio/journey
 * fields on top of the existing Mentor Knowledge Base), book a session
 * or send a lighter guidance request, save an expert for later, and
 * register for upcoming Experience Events. No new AI reasoning; slots
 * are deterministically generated illustrative times, not a real
 * calendar.
 */
export function ExpertConnectScreen() {
  const {
    experts, events, registrations, savedExpertIds, isBusy,
    bookSession, requestGuidance, toggleSaveExpert, registerForEvent,
  } = useCareerExperienceContext();
  const [selected, setSelected] = useState<MentorSummary | null>(null);
  const [detail, setDetail] = useState<MentorDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [topic, setTopic] = useState("");
  const [guidanceMessage, setGuidanceMessage] = useState("");
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    setIsLoadingDetail(true);
    setSelectedSlot(null);
    setTopic("");
    setGuidanceMessage("");
    setActionFeedback(null);
    apiClient
      .get<MentorDetail>(`/v1/mentors/${selected.id}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setIsLoadingDetail(false));
  }, [selected]);

  const registeredEventIds = new Set(registrations.map((r) => r.event_id));

  if (selected) {
    const isSaved = savedExpertIds.includes(selected.id);

    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <button onClick={() => setSelected(null)} className="text-xs text-ink-faint hover:text-ink-muted">
          ← Experts
        </button>

        <div className="mt-2 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-light text-ink">{selected.name}</h1>
            <p className="mt-1 text-sm text-ink-muted">
              {selected.role_type} · {selected.field}
              {selected.organization && ` · ${selected.organization}`}
            </p>
          </div>
          <Button
            variant="ghost"
            onClick={() => toggleSaveExpert(selected.id)}
            className={cn(isSaved && "text-accent-soft")}
          >
            <Heart size={14} className={cn(isSaved && "fill-current")} /> {isSaved ? "Saved" : "Save Expert"}
          </Button>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-ink-muted">{selected.bio}</p>
        {selected.years_experience > 0 && (
          <p className="mt-1 text-xs text-ink-faint">{selected.years_experience} years of experience</p>
        )}

        {selected.journey_highlights.length > 0 && (
          <section className="mt-6">
            <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Journey Highlights</p>
            <ul className="space-y-1.5 text-sm text-ink-muted">
              {selected.journey_highlights.map((h, i) => (
                <li key={i}>• {h}</li>
              ))}
            </ul>
          </section>
        )}

        {selected.discussion_topics.length > 0 && (
          <section className="mt-6">
            <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Discussion Topics</p>
            <div className="flex flex-wrap gap-1.5">
              {selected.discussion_topics.map((t) => (
                <Badge key={t} tone="cool">{t}</Badge>
              ))}
            </div>
          </section>
        )}

        {isLoadingDetail && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {detail && (
          <>
            <section className="mt-8">
              <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Book a Session</p>
              {detail.available_slots.length === 0 ? (
                <p className="text-xs text-ink-faint">No slots available right now.</p>
              ) : (
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                  {detail.available_slots.map((slot) => (
                    <button
                      key={slot}
                      onClick={() => setSelectedSlot(slot)}
                      className={cn(
                        "rounded-lg border px-3 py-2 text-left text-xs transition",
                        selectedSlot === slot
                          ? "border-accent/40 bg-accent/10 text-accent-soft"
                          : "border-border text-ink-muted hover:text-ink",
                      )}
                    >
                      {new Date(slot).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}
                    </button>
                  ))}
                </div>
              )}

              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="What would you like to discuss?"
                className="mt-3"
              />
              <Button
                className="mt-3"
                disabled={!selectedSlot || !topic.trim() || isBusy}
                onClick={async () => {
                  if (!selectedSlot) return;
                  await bookSession(selected.id, selectedSlot, topic.trim());
                  setActionFeedback("Session requested — this is a real, student-initiated request, not an auto-accepted booking.");
                  setSelectedSlot(null);
                  setTopic("");
                }}
              >
                Book Session
              </Button>
            </section>

            <section className="mt-8">
              <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Request Guidance</p>
              <p className="mb-2 text-xs text-ink-faint">
                A lighter alternative to booking a specific time — send a message instead.
              </p>
              <Input
                value={guidanceMessage}
                onChange={(e) => setGuidanceMessage(e.target.value)}
                placeholder="What guidance are you looking for?"
              />
              <Button
                variant="ghost"
                className="mt-3"
                disabled={!guidanceMessage.trim() || isBusy}
                onClick={async () => {
                  await requestGuidance(selected.id, guidanceMessage.trim());
                  setActionFeedback("Guidance request sent.");
                  setGuidanceMessage("");
                }}
              >
                Request Guidance
              </Button>
            </section>

            {actionFeedback && <p className="mt-4 text-xs text-accent-soft">{actionFeedback}</p>}

            {detail.upcoming_career_talks.length > 0 && (
              <section className="mt-8">
                <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">
                  {selected.name}'s Experience Events
                </p>
                <div className="space-y-2">
                  {detail.upcoming_career_talks.map((event) => (
                    <EventRow
                      key={event.id}
                      event={event}
                      isRegistered={registeredEventIds.has(event.id)}
                      isBusy={isBusy}
                      onRegister={() => registerForEvent(event.id)}
                    />
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Expert Connect</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Real mentors, built on top of Mentor Intelligence — book a session, request guidance, or
        save an expert for later.
      </p>

      {experts.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel icon={Users} title="No Experts Yet" description="Aureon's mentor pool hasn't been populated yet — check back once it has." />
        </div>
      ) : (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {experts.map((mentor) => {
            const isSaved = savedExpertIds.includes(mentor.id);
            return (
              <Surface key={mentor.id} tone="raised" padding="md" className="flex h-full flex-col">
                <button onClick={() => setSelected(mentor)} className="text-left">
                  <p className="text-sm font-medium text-ink">{mentor.name}</p>
                  <p className="mt-1 text-xs text-ink-faint">
                    {mentor.role_type} · {mentor.field}
                  </p>
                </button>
                <div className="mt-auto flex items-center justify-between pt-3">
                  <button onClick={() => setSelected(mentor)} className="text-xs text-accent-soft hover:text-accent">
                    View profile →
                  </button>
                  <button
                    onClick={() => toggleSaveExpert(mentor.id)}
                    className={cn("text-ink-faint transition hover:text-ink", isSaved && "text-accent-soft")}
                    aria-label={isSaved ? "Unsave expert" : "Save expert"}
                  >
                    <Heart size={16} className={cn(isSaved && "fill-current")} />
                  </button>
                </div>
              </Surface>
            );
          })}
        </div>
      )}

      {events.length > 0 && (
        <div className="mt-10">
          <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Experience Events</p>
          <div className="space-y-2">
            {events.map((event) => (
              <EventRow
                key={event.id}
                event={event}
                isRegistered={registeredEventIds.has(event.id)}
                isBusy={isBusy}
                onRegister={() => registerForEvent(event.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function EventRow({
  event,
  isRegistered,
  isBusy,
  onRegister,
}: {
  event: { id: string; title: string; event_type: string; description: string; scheduled_at: string };
  isRegistered: boolean;
  isBusy: boolean;
  onRegister: () => void;
}) {
  return (
    <Surface tone="raised" padding="sm" className="flex items-center justify-between gap-4">
      <div>
        <div className="flex items-center gap-2">
          <CalendarDays size={14} className="text-ink-faint" />
          <p className="text-sm text-ink">{event.title}</p>
          <Badge tone="cool">{event.event_type.replace("_", " ")}</Badge>
        </div>
        <p className="mt-1 text-xs text-ink-muted">{event.description}</p>
        <p className="mt-1 text-[0.7rem] text-ink-faint">
          {new Date(event.scheduled_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}
        </p>
      </div>
      <Button variant={isRegistered ? "ghost" : "primary"} disabled={isRegistered || isBusy} onClick={onRegister}>
        {isRegistered ? "Registered" : "Register"}
      </Button>
    </Surface>
  );
}
