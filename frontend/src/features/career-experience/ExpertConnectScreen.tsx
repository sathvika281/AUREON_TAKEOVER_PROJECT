import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Handshake, Heart, Sparkles, Users } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { NextBestAction, type NextBestActionSuggestion } from "../../design-system/components/NextBestAction";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import { apiClient } from "../../shared/api/client";
import type {
  ExpertDetail,
  ExpertFiltersResponse,
  ExpertSearchResponse,
  ExpertSummary,
  MentorMatch,
} from "../../shared/api/types";
import { useDecisionContext } from "../decision/DecisionContext";
import { MentorMatchCard } from "../decision/MentorMatchCard";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { useCareerExperienceContext } from "./CareerExperienceContext";
import { ExpertConnectTabs } from "./ExpertConnectTabs";

function deriveNextBestAction(matches: MentorMatch[], confidenceScore: number): NextBestActionSuggestion {
  if (matches.length > 0) {
    const top = matches[0];
    return {
      action: `Ask ${top.mentor_name} a question`,
      reason: top.why_it_matches,
    };
  }
  if (confidenceScore < 0.7) {
    return {
      action: "Ask a mentor a question",
      reason: `Your confidence is at ${Math.round(confidenceScore * 100)}% — a real conversation with someone in the field can sharpen it faster than reading alone.`,
    };
  }
  return {
    action: "Browse Aureon's expert pool",
    reason: "See who's available to talk to, or run a match to find mentors reasoned against your Career DNA.",
  };
}

function PillToggle({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-3.5 py-1.5 text-xs transition-colors",
        active
          ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
          : "border-border text-ink-muted hover:border-border-strong hover:text-ink",
      )}
    >
      {label}
    </button>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <section className="mt-6">
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <ul className="space-y-1.5 text-sm text-ink-muted">
        {items.map((item, i) => (
          <li key={i}>• {item}</li>
        ))}
      </ul>
    </section>
  );
}

function ParagraphSection({ title, text }: { title: string; text: string }) {
  if (!text) return null;
  return (
    <section className="mt-6">
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <p className="text-sm leading-relaxed text-ink-muted">{text}</p>
    </section>
  );
}

/**
 * Expert Connect — search and filter Aureon's real expert pool (an
 * expert IS a Mentor; see `/v1/experts`, wrapping the same `mentors`
 * table with richer profile/journey/reality/knowledge fields), view a
 * full profile, book a session or send a lighter guidance request,
 * save an expert for later, and register for upcoming Experience
 * Events. No new AI reasoning; slots are deterministically generated
 * illustrative times, not a real calendar.
 */
export function ExpertConnectScreen() {
  const {
    events, registrations, savedExpertIds, mentorships, isBusy,
    bookSession, requestGuidance, toggleSaveExpert, registerForEvent, requestMentorship,
    ensureLoaded,
  } = useCareerExperienceContext();
  const { confidenceScore } = useDiscoveryContext();
  const {
    mentorMatches, isBusy: isMatching, error: matchError, analyzeMentors, lastMentorMission,
    ensureMentorMatchesLoaded, isMentorMatchesLoading,
  } = useDecisionContext();

  const [expertSummaries, setExpertSummaries] = useState<ExpertSummary[]>([]);
  const [filters, setFilters] = useState<ExpertFiltersResponse | null>(null);
  const [query, setQuery] = useState("");
  const [specializationFilter, setSpecializationFilter] = useState<string | null>(null);
  const [industryFilter, setIndustryFilter] = useState<string | null>(null);
  const [countryFilter, setCountryFilter] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ExpertDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [topic, setTopic] = useState("");
  const [guidanceMessage, setGuidanceMessage] = useState("");
  const [mentorshipGoals, setMentorshipGoals] = useState("");
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  useEffect(() => {
    ensureLoaded();
    ensureMentorMatchesLoaded();
    apiClient
      .get<ExpertSearchResponse>("/v1/experts?limit=200")
      .then((r) => setExpertSummaries(r.experts))
      .catch(() => {});
    apiClient
      .get<ExpertFiltersResponse>("/v1/experts/filters")
      .then(setFilters)
      .catch(() => {});
  }, [ensureLoaded, ensureMentorMatchesLoaded]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    setIsLoadingDetail(true);
    setSelectedSlot(null);
    setTopic("");
    setGuidanceMessage("");
    setMentorshipGoals("");
    setActionFeedback(null);
    apiClient
      .get<ExpertDetail>(`/v1/experts/${selectedId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setIsLoadingDetail(false));
  }, [selectedId]);

  const filteredExperts = useMemo(() => {
    const q = query.trim().toLowerCase();
    return expertSummaries.filter((e) => {
      if (q) {
        const haystack = `${e.name} ${e.profession} ${e.specialization}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (specializationFilter && e.specialization !== specializationFilter) return false;
      if (industryFilter && !e.industries.includes(industryFilter)) return false;
      if (countryFilter && e.country !== countryFilter) return false;
      return true;
    });
  }, [expertSummaries, query, specializationFilter, industryFilter, countryFilter]);

  const registeredEventIds = new Set(registrations.map((r) => r.event_id));

  if (selectedId) {
    const isSaved = savedExpertIds.includes(selectedId);

    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <ExpertConnectTabs />
        <button onClick={() => setSelectedId(null)} className="mt-6 text-xs text-ink-faint hover:text-ink-muted">
          ← Experts
        </button>

        {isLoadingDetail && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {detail && (
          <>
            <div className="mt-2 flex items-start justify-between gap-4">
              <div>
                <h1 className="text-2xl font-light text-ink">{detail.name}</h1>
                <p className="mt-1 text-sm text-ink-muted">
                  {detail.profession || detail.role_type} · {detail.specialization || detail.field}
                  {detail.organization && ` · ${detail.organization}`}
                </p>
                {(detail.country || detail.city) && (
                  <p className="mt-0.5 text-xs text-ink-faint">
                    {[detail.city, detail.country].filter(Boolean).join(", ")}
                  </p>
                )}
              </div>
              <Button
                variant="ghost"
                onClick={() => toggleSaveExpert(detail.id)}
                className={cn(isSaved && "text-accent-soft")}
              >
                <Heart size={14} className={cn(isSaved && "fill-current")} /> {isSaved ? "Saved" : "Save Expert"}
              </Button>
            </div>

            {detail.who_should_talk_to_me.length > 0 && (
              <Surface tone="raised" padding="sm" className="mt-4">
                <div className="flex items-center gap-1.5 text-accent-soft">
                  <Sparkles size={13} />
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em]">Who Should Talk to Me</p>
                </div>
                <ul className="mt-2 space-y-1 text-sm text-ink-muted">
                  {detail.who_should_talk_to_me.map((w, i) => (
                    <li key={i}>• {w}</li>
                  ))}
                </ul>
              </Surface>
            )}

            <p className="mt-4 text-sm leading-relaxed text-ink-muted">{detail.bio}</p>
            <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-faint">
              {detail.years_experience > 0 && <span>{detail.years_experience} years of experience</span>}
              <span>Profile last updated {new Date(detail.updated_at).toLocaleDateString(undefined, { month: "long", year: "numeric" })}</span>
            </div>

            {detail.linked_careers.length > 0 && (
              <section className="mt-6">
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Related Careers</p>
                <div className="flex flex-wrap gap-1.5">
                  {detail.linked_careers.map((c) => (
                    <Badge key={c.id} tone="cool">{c.name}</Badge>
                  ))}
                </div>
              </section>
            )}

            {detail.career_journey.length > 0 && (
              <section className="mt-8">
                <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Career Journey</p>
                <div className="space-y-3 border-l border-border pl-4">
                  {detail.career_journey.map((m, i) => (
                    <div key={i}>
                      <div className="flex items-center gap-2">
                        <Badge tone="warm">{m.stage.replace(/_/g, " ")}</Badge>
                        <span className="text-xs text-ink-faint">{m.year_label}</span>
                      </div>
                      <p className="mt-1 text-sm text-ink">{m.label}</p>
                      <p className="text-xs text-ink-muted">{m.description}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section className="mt-8">
              <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Reality</p>
              <ParagraphSection title="Day in the Life" text={detail.day_in_the_life} />
              <ParagraphSection title="Weekly Routine" text={detail.weekly_routine} />
              <ListSection title="Biggest Challenges" items={detail.biggest_challenges} />
              <ParagraphSection title="Favourite Part" text={detail.favourite_part} />
              <ListSection title="Biggest Misconceptions" items={detail.biggest_misconceptions} />
              <ParagraphSection title="What Surprised Them" text={detail.what_surprised_them} />
              <ParagraphSection title="Biggest Mistake" text={detail.biggest_mistake} />
              <ParagraphSection title="One Regret" text={detail.one_regret} />
              <ParagraphSection title="Salary Reality" text={detail.salary_reality} />
              <ParagraphSection title="Work-Life Balance" text={detail.work_life_balance} />
              <ListSection title="Skills Used Daily" items={detail.daily_skills} />
              <ListSection title="Tools Used Daily" items={detail.daily_tools} />
              <ListSection title="Recommended Books" items={detail.recommended_books} />
              <ListSection title="Recommended Communities" items={detail.recommended_communities} />
              <ParagraphSection title="Advice for Beginners" text={detail.advice_for_beginners} />

              {detail.faqs.length > 0 && (
                <section className="mt-6">
                  <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">FAQs</p>
                  <div className="space-y-3">
                    {detail.faqs.map((f, i) => (
                      <div key={i}>
                        <p className="text-sm text-ink">{f.question}</p>
                        <p className="mt-0.5 text-xs text-ink-muted">{f.answer}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </section>

            <section className="mt-8">
              <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Knowledge</p>
              <ListSection title="Projects" items={detail.projects} />
              <ListSection title="Research" items={detail.research} />
              <ListSection title="Certifications" items={detail.certifications} />
              <ListSection title="Conferences" items={detail.conferences} />
              <ListSection title="Organizations" items={detail.organizations} />
              <ListSection title="Volunteer Work" items={detail.volunteer_work} />
              <ListSection title="Suggested Books (from linked careers)" items={detail.suggested_books} />
              <ListSection title="Suggested Companies (from linked careers)" items={detail.suggested_companies} />
              <ListSection title="Suggested Certifications (from linked careers)" items={detail.suggested_certifications} />

              {(detail.portfolio_links.length > 0 || detail.social_links.length > 0) && (
                <section className="mt-6">
                  <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Links</p>
                  <div className="flex flex-wrap gap-2">
                    {[...detail.portfolio_links, ...detail.social_links].map((link, i) => (
                      <a
                        key={i}
                        href={link.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-accent-soft hover:text-accent"
                      >
                        {link.label} →
                      </a>
                    ))}
                  </div>
                </section>
              )}
            </section>

            <section className="mt-8">
              <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Book a Session</p>
              {detail.available_slots.length === 0 ? (
                <p className="text-xs text-ink-faint">No slots available right now.</p>
              ) : (
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                  {detail.available_slots.map((slot) => (
                    <button
                      key={slot}
                      onClick={() => setSelectedSlot(slot)}
                      className={cn(
                        "rounded-lg border px-3 py-2 text-left text-xs transition-colors",
                        selectedSlot === slot
                          ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                          : "border-border text-ink-muted hover:border-border-strong hover:text-ink",
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
                  await bookSession(detail.id, selectedSlot, topic.trim());
                  setActionFeedback("Session requested — this is a real, student-initiated request, not an auto-accepted booking.");
                  setSelectedSlot(null);
                  setTopic("");
                }}
              >
                Book Session
              </Button>
            </section>

            <section className="mt-8">
              <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Request Guidance</p>
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
                  await requestGuidance(detail.id, guidanceMessage.trim());
                  setActionFeedback("Guidance request sent.");
                  setGuidanceMessage("");
                }}
              >
                Request Guidance
              </Button>
            </section>

            {detail.accepts_mentorship && (() => {
              const existing = mentorships
                .filter((m) => m.expert_id === detail.id)
                .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0];
              const atCapacity = detail.max_students > 0 && detail.current_mentee_count >= detail.max_students;

              return (
                <section className="mt-8">
                  <div className="mb-2 flex items-center gap-1.5 px-1 text-accent-soft">
                    <Handshake size={13} />
                    <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em]">Mentorship</p>
                  </div>
                  <p className="mb-2 text-xs text-ink-faint">
                    A real relationship, not a single conversation — {detail.name} reviews your request and
                    can accept, decline, or discuss goals and progress over time.
                    {detail.max_students > 0 && (
                      <> Currently mentoring {detail.current_mentee_count} of {detail.max_students} students.</>
                    )}
                  </p>
                  {existing?.status === "requested" ? (
                    <Badge tone="warm">Pending — Waiting for Mentor</Badge>
                  ) : existing?.status === "accepted" ? (
                    <Badge tone="success">Accepted — Your Mentor</Badge>
                  ) : (
                    <>
                      {existing?.status === "declined" && (
                        <p className="mb-2 text-xs text-ink-faint">
                          Your previous request was declined — you're welcome to send a new one.
                        </p>
                      )}
                      {existing?.status === "completed" && (
                        <p className="mb-2 text-xs text-ink-faint">
                          Your mentorship with {detail.name} was marked complete — you're welcome to request again.
                        </p>
                      )}
                      {atCapacity ? (
                        <p className="text-xs text-ink-muted">
                          {detail.name} isn't currently taking new mentees — check back later.
                        </p>
                      ) : (
                        <>
                          <Input
                            value={mentorshipGoals}
                            onChange={(e) => setMentorshipGoals(e.target.value)}
                            placeholder="What are you hoping to work on together?"
                          />
                          <Button
                            variant="ghost"
                            className="mt-3"
                            disabled={!mentorshipGoals.trim() || isBusy}
                            onClick={async () => {
                              await requestMentorship(detail.id, mentorshipGoals.trim());
                              setActionFeedback("Mentorship requested — the expert will review and respond.");
                              setMentorshipGoals("");
                            }}
                          >
                            Request as Mentor
                          </Button>
                        </>
                      )}
                    </>
                  )}
                </section>
              );
            })()}

            {actionFeedback && <p className="mt-4 text-xs text-accent-soft">{actionFeedback}</p>}

            {detail.upcoming_career_talks.length > 0 && (
              <section className="mt-8">
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  {detail.name}'s Experience Events
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
      <ExpertConnectTabs />
      <h1 className="mt-6 text-2xl font-light text-ink">Expert Connect</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Who can guide me? Real experts, built on top of Mentor Intelligence — matched to your
        Career DNA, searched and filtered openly, booked, or saved for later.
      </p>

      <div className="mt-6">
        <NextBestAction suggestion={deriveNextBestAction(mentorMatches, confidenceScore)} />
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Matched For You</p>
          <Button size="md" onClick={analyzeMentors} disabled={isMatching}>
            {isMatching ? "Matching…" : mentorMatches.length > 0 ? "Re-run Match" : "Find My Matches"}
          </Button>
        </div>
        {matchError && <p className="mt-2 text-xs text-danger">{matchError}</p>}
        {isMentorMatchesLoading ? (
          <p className="mt-3 text-sm text-ink-faint">Loading…</p>
        ) : mentorMatches.length === 0 ? (
          <div className="mt-3">
            <EmptyStatePanel
              icon={Users}
              title="No Mentor Matches Yet"
              description="Run the match above to see mentors reasoned against your real Career DNA — this requires enough evidence for Aureon to reason about fit responsibly."
            />
          </div>
        ) : (
          <div className="mt-3 space-y-3">
            {mentorMatches.map((m) => (
              <MentorMatchCard key={m.mentor_id} match={m} />
            ))}
            {lastMentorMission && lastMentorMission.stages.length > 0 && (
              <p className="text-[0.65rem] text-ink-faint">
                Reasoned across {lastMentorMission.stages.length} real stages — see Journey for the full mission.
              </p>
            )}
          </div>
        )}
      </div>

      <p className="mb-3 mt-10 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Explore All Experts
      </p>

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by name, profession, or specialization…"
      />

      {filters && (filters.specializations.length > 0 || filters.industries.length > 0 || filters.countries.length > 0) && (
        <div className="mt-3 space-y-2">
          {filters.specializations.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {filters.specializations.map((s) => (
                <PillToggle
                  key={s}
                  label={s}
                  active={specializationFilter === s}
                  onClick={() => setSpecializationFilter(specializationFilter === s ? null : s)}
                />
              ))}
            </div>
          )}
          {filters.industries.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {filters.industries.map((s) => (
                <PillToggle
                  key={s}
                  label={s}
                  active={industryFilter === s}
                  onClick={() => setIndustryFilter(industryFilter === s ? null : s)}
                />
              ))}
            </div>
          )}
          {filters.countries.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {filters.countries.map((s) => (
                <PillToggle
                  key={s}
                  label={s}
                  active={countryFilter === s}
                  onClick={() => setCountryFilter(countryFilter === s ? null : s)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {filteredExperts.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel icon={Users} title="No Experts Found" description="Try clearing a filter or searching a different term." />
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {filteredExperts.map((expert) => {
            const isSaved = savedExpertIds.includes(expert.id);
            return (
              <Surface key={expert.id} tone="raised" padding="md" className="flex h-full flex-col">
                <button onClick={() => setSelectedId(expert.id)} className="text-left">
                  <p className="text-sm font-medium text-ink">{expert.name}</p>
                  <p className="mt-1 text-xs text-ink-faint">
                    {expert.profession || "—"}{expert.specialization && ` · ${expert.specialization}`}
                  </p>
                  {expert.country && <p className="mt-0.5 text-[0.7rem] text-ink-faint">{expert.country}</p>}
                  {expert.who_should_talk_to_me.length > 0 && (
                    <p className="mt-2 text-xs italic text-ink-muted">"{expert.who_should_talk_to_me[0]}"</p>
                  )}
                </button>
                <div className="mt-auto flex items-center justify-between pt-3">
                  <button onClick={() => setSelectedId(expert.id)} className="text-xs text-accent-soft hover:text-accent">
                    View profile →
                  </button>
                  <button
                    onClick={() => toggleSaveExpert(expert.id)}
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
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Experience Events</p>
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
