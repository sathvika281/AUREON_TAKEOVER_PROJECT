import { useEffect, useMemo, useState } from "react";
import { Building2, CalendarDays, Compass } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { NextBestAction, type NextBestActionSuggestion } from "../../design-system/components/NextBestAction";
import { StarRating } from "../../design-system/components/StarRating";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { CollegeMatch, InstitutionDetail, InstitutionSummary } from "../../shared/api/types";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { traitLabel } from "../discovery/network/layoutTraits";
import { CollegeMatchCard } from "../decision/CollegeMatchCard";
import { useDecisionContext } from "../decision/DecisionContext";
import { useCareerExperienceContext } from "./CareerExperienceContext";

function deriveNextBestAction(matches: CollegeMatch[]): NextBestActionSuggestion {
  if (matches.length >= 2) {
    const [a, b] = matches;
    return {
      action: `Compare ${a.institution_name} with ${b.institution_name}`,
      reason: `Both matched to you — ${a.institution_name}: ${a.why_it_matches.slice(0, 80)}${a.why_it_matches.length > 80 ? "…" : ""}`,
    };
  }
  if (matches.length === 1) {
    return {
      action: `Explore ${matches[0].institution_name}`,
      reason: matches[0].why_it_matches,
    };
  }
  return {
    action: "Find institutions matched to you",
    reason: "Aureon can reason about fit against your real Career DNA once you run the match below.",
  };
}

/**
 * College Explorer — where should I study? Browse Aureon's real,
 * full institution catalog (not partner-only), see real institutions
 * matched to you (moved here from the old Guiding Stars/mentor-match
 * screen), and drill into each institution's real research, innovation,
 * faculty, ambassador, and student project data where it genuinely
 * exists. Built entirely on top of Institution Intelligence; no new AI
 * reasoning happens for the catalog browse itself.
 */
export function CollegeCollaborationScreen() {
  const { institutions, events, registrations, registerForEvent, isBusy } = useCareerExperienceContext();
  const { careerDna } = useDiscoveryContext();
  const { collegeMatches, isBusy: isMatching, error, analyzeColleges, lastCollegeMission } = useDecisionContext();
  const [selected, setSelected] = useState<InstitutionSummary | null>(null);
  const [detail, setDetail] = useState<InstitutionDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    setIsLoadingDetail(true);
    apiClient
      .get<InstitutionDetail>(`/v1/institutions/${selected.id}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setIsLoadingDetail(false));
  }, [selected]);

  const registeredEventIds = new Set(registrations.map((r) => r.event_id));
  const filteredInstitutions = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return institutions;
    return institutions.filter(
      (inst) =>
        inst.name.toLowerCase().includes(q) ||
        inst.city.toLowerCase().includes(q) ||
        inst.country.toLowerCase().includes(q),
    );
  }, [institutions, query]);

  if (selected) {
    const dnaOverlap = detail
      ? detail.trait_tags.filter((t) => t in careerDna).map(traitLabel)
      : [];

    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <button
          onClick={() => setSelected(null)}
          className="text-xs text-ink-faint transition-colors hover:text-ink-muted"
        >
          ← College Explorer
        </button>

        <p className="mt-4 font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">
          The Nearby Worlds Observatory
        </p>
        <div className="mt-2 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-light text-ink">{selected.name}</h1>
            <p className="mt-1 text-sm text-ink-muted">{selected.city}, {selected.country}</p>
          </div>
          {selected.is_partner && <Badge tone="warm">Collaborating Educational Organization</Badge>}
        </div>

        {isLoadingDetail && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {detail?.profile && (
          <Surface tone="raised" padding="md" className="mt-6 space-y-2.5">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
              Profile — based on available opportunities, not a ranking
            </p>
            <StarRating label="Research" value={detail.profile.research} />
            <StarRating label="Entrepreneurship" value={detail.profile.entrepreneurship} />
            <StarRating label="Campus Life" value={detail.profile.campus_life} />
            <StarRating label="International Exposure" value={detail.profile.international_exposure} />
          </Surface>
        )}

        {detail && (
          <div className="mt-8 space-y-8">
            <section>
              <p className="text-sm leading-relaxed text-ink-muted">{detail.research_culture}</p>
            </section>

            {(detail.hostels.length > 0 || detail.exchange_programs.length > 0 || detail.campus_facilities.length > 0) && (
              <section className="space-y-4">
                {detail.hostels.length > 0 && (
                  <div>
                    <p className="mb-1.5 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Hostels</p>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.hostels.map((h) => (
                        <Badge key={h} tone="cool">{h}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {detail.exchange_programs.length > 0 && (
                  <div>
                    <p className="mb-1.5 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Exchange Programs</p>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.exchange_programs.map((e) => (
                        <Badge key={e} tone="cool">{e}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {detail.campus_facilities.length > 0 && (
                  <div>
                    <p className="mb-1.5 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Campus Facilities</p>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.campus_facilities.map((f) => (
                        <Badge key={f} tone="cool">{f}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

            {detail.student_reviews.length > 0 && (
              <section>
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  Student Reviews
                </p>
                <div className="space-y-2">
                  {detail.student_reviews.map((review) => (
                    <Surface key={review.quote} tone="raised" padding="sm">
                      <p className="text-sm leading-relaxed text-ink-muted">&ldquo;{review.quote}&rdquo;</p>
                      <p className="mt-2 text-[0.7rem] text-ink-faint">
                        — {review.role_label}
                        {review.sentiment === "mixed" && <span className="ml-1.5 text-ink-faint">(mixed feedback)</span>}
                      </p>
                    </Surface>
                  ))}
                </div>
              </section>
            )}

            {(detail.campus_life_and_culture || detail.fees_summary || detail.scholarships_summary) && (
              <section className="space-y-4">
                {detail.campus_life_and_culture && (
                  <div>
                    <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                      Campus Life &amp; Culture
                    </p>
                    <p className="text-sm leading-relaxed text-ink-muted">{detail.campus_life_and_culture}</p>
                  </div>
                )}
                {detail.fees_summary && (
                  <div>
                    <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Fees</p>
                    <p className="text-sm leading-relaxed text-ink-muted">{detail.fees_summary}</p>
                  </div>
                )}
                {detail.scholarships_summary && (
                  <div>
                    <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                      Scholarships
                    </p>
                    <p className="text-sm leading-relaxed text-ink-muted">{detail.scholarships_summary}</p>
                  </div>
                )}
              </section>
            )}

            {detail.entrance_exams.length > 0 && (
              <section>
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  Entrance Exams
                </p>
                <div className="space-y-2">
                  {detail.entrance_exams.map((exam) => (
                    <Surface key={exam.id} tone="raised" padding="sm">
                      <p className="text-sm text-ink">{exam.name}</p>
                      <p className="mt-1 text-xs text-ink-muted">{exam.description}</p>
                      {exam.eligibility.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {exam.eligibility.map((e) => (
                            <Badge key={e} tone="cool">{e}</Badge>
                          ))}
                        </div>
                      )}
                      <p className="mt-2 text-[0.7rem] text-ink-faint">
                        Preparation: {exam.preparation_guidance}
                      </p>
                      <p className="mt-1 text-[0.7rem] text-ink-faint">Timeline: {exam.typical_timeline}</p>
                    </Surface>
                  ))}
                </div>
              </section>
            )}

            <SectionList
              title="Research Labs"
              items={detail.research_labs.map((l) => ({ id: l.id, name: l.name, description: l.description, meta: l.focus_area }))}
            />
            <SectionList
              title="Innovation Centers"
              items={detail.innovation_centers.map((c) => ({ id: c.id, name: c.name, description: c.description, meta: c.focus_area }))}
            />
            <SectionList
              title="Faculty Highlights"
              items={detail.faculty_highlights.map((f) => ({ id: f.id, name: `${f.name} — ${f.title}`, description: f.bio, meta: f.expertise_area }))}
            />
            <SectionList
              title="Student Ambassadors"
              items={detail.student_ambassadors.map((a) => ({ id: a.id, name: a.student_label, description: a.message, meta: a.program }))}
            />
            <SectionList
              title="Student Project Showcase"
              items={detail.student_projects.map((p) => ({
                id: p.id,
                name: `${p.student_label} — ${p.project_title}`,
                description: p.description,
                meta: p.skills_used.join(", "),
              }))}
            />
            <SectionList
              title="Internship Opportunities"
              items={detail.internship_opportunities.map((i) => ({ id: i.id, name: i.title, description: i.description, meta: i.field }))}
            />

            <section>
              <div className="mb-2 flex items-center justify-between px-1">
                <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Academic Programs</p>
                {dnaOverlap.length > 0 && (
                  <span className="text-[0.65rem] text-accent-soft">
                    Aligned with your Career DNA: {dnaOverlap.join(", ")}
                  </span>
                )}
              </div>
              {detail.academic_programs.length === 0 ? (
                <p className="text-xs text-ink-faint">No academic programs listed yet.</p>
              ) : (
                <div className="space-y-2">
                  {detail.academic_programs.map((p) => (
                    <Surface key={p.id} tone="raised" padding="sm">
                      <p className="text-sm text-ink">{p.name} <span className="text-ink-faint">— {p.degree_type}</span></p>
                      <p className="mt-1 text-xs text-ink-muted">{p.description}</p>
                    </Surface>
                  ))}
                </div>
              )}
            </section>

            <section>
              <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Experience Events at {detail.name}
              </p>
              {detail.upcoming_events.length === 0 ? (
                <p className="text-xs text-ink-faint">No events scheduled right now.</p>
              ) : (
                <div className="space-y-2">
                  {detail.upcoming_events.map((event) => (
                    <EventRow
                      key={event.id}
                      event={event}
                      isRegistered={registeredEventIds.has(event.id)}
                      isBusy={isBusy}
                      onRegister={() => registerForEvent(event.id)}
                    />
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">
        The Nearby Worlds Observatory
      </p>
      <h1 className="mt-2 text-2xl font-light text-ink">College Explorer</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Where should I study? Real institutions, real research, real programs — browsed openly or
        matched against your own Career DNA.
      </p>

      <div className="mt-6">
        <NextBestAction suggestion={deriveNextBestAction(collegeMatches)} />
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Matched For You</p>
          <Button size="md" onClick={analyzeColleges} disabled={isMatching}>
            {isMatching ? "Matching…" : collegeMatches.length > 0 ? "Re-run Match" : "Find My Matches"}
          </Button>
        </div>
        {error && <p className="mt-2 text-xs text-danger">{error}</p>}
        {collegeMatches.length === 0 ? (
          <div className="mt-3">
            <EmptyStatePanel
              icon={Compass}
              title="No Institution Matches Yet"
              description="Run the match above to see institutions reasoned against your real Career DNA — this requires enough evidence for Aureon to reason about fit responsibly."
            />
          </div>
        ) : (
          <div className="mt-3 space-y-3">
            {collegeMatches.map((m) => (
              <CollegeMatchCard key={m.institution_id} match={m} />
            ))}
            {lastCollegeMission && lastCollegeMission.stages.length > 0 && (
              <p className="text-[0.65rem] text-ink-faint">
                Reasoned across {lastCollegeMission.stages.length} real stages — see Journey for the full mission.
              </p>
            )}
          </div>
        )}
      </div>

      <div className="mt-10">
        <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
          Explore All Institutions
        </p>
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, city, or country…"
        />

        {filteredInstitutions.length === 0 ? (
          <div className="mt-4">
            <EmptyStatePanel
              icon={Building2}
              title={institutions.length === 0 ? "No Institutions Yet" : "No Matches for This Search"}
              description={
                institutions.length === 0
                  ? "Aureon's institution catalog hasn't been populated yet — check back once it has."
                  : "Try a different name, city, or country."
              }
            />
          </div>
        ) : (
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {filteredInstitutions.map((inst) => (
              <button key={inst.id} onClick={() => setSelected(inst)} className="text-left">
                <Surface tone="raised" padding="md" className="h-full transition-colors hover:border-accent-soft/40">
                  <div className="flex items-center gap-2.5">
                    <span className="relative inline-flex h-3.5 w-3.5 shrink-0 items-center justify-center">
                      <span className="absolute inset-0 rounded-full border border-accent-soft/60" />
                      <span className="h-1 w-1 rounded-full bg-accent-soft" />
                    </span>
                    <p className="flex-1 text-sm font-medium text-ink">{inst.name}</p>
                    {inst.is_partner && <Badge tone="warm">Partner</Badge>}
                  </div>
                  <p className="mt-1.5 pl-6 text-xs text-ink-faint">{inst.city}, {inst.country}</p>
                  {inst.trait_tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5 pl-6">
                      {inst.trait_tags.slice(0, 4).map((t) => (
                        <Badge key={t} tone="cool">{traitLabel(t)}</Badge>
                      ))}
                    </div>
                  )}
                </Surface>
              </button>
            ))}
          </div>
        )}
      </div>

      {events.length > 0 && (
        <div className="mt-10">
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Experience Events</p>
          <div className="space-y-2">
            {events
              .filter((e) => e.institution_id)
              .map((event) => (
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

function SectionList({
  title,
  items,
}: {
  title: string;
  items: { id: string; name: string; description: string; meta: string }[];
}) {
  if (items.length === 0) return null;
  return (
    <section>
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <div className="space-y-2">
        {items.map((item) => (
          <Surface key={item.id} tone="raised" padding="sm">
            <p className="text-sm text-ink">{item.name}</p>
            <p className="mt-1 text-xs text-ink-muted">{item.description}</p>
            {item.meta && <p className="mt-1 text-[0.7rem] text-ink-faint">{item.meta}</p>}
          </Surface>
        ))}
      </div>
    </section>
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
