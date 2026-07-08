import { useEffect, useState } from "react";
import { Building2, CalendarDays } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { InstitutionDetail, InstitutionSummary } from "../../shared/api/types";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { traitLabel } from "../discovery/network/layoutTraits";
import { useCareerExperienceContext } from "./CareerExperienceContext";

/**
 * College Collaboration — browse Aureon's collaborating educational
 * organizations (partner-flagged Institution rows) and drill into each
 * one's real research, innovation, faculty, ambassador, and student
 * project data. Built entirely on top of Institution Intelligence; no
 * new AI reasoning happens here.
 */
export function CollegeCollaborationScreen() {
  const { partnerColleges, events, registrations, registerForEvent, isBusy } = useCareerExperienceContext();
  const { careerDna } = useDiscoveryContext();
  const [selected, setSelected] = useState<InstitutionSummary | null>(null);
  const [detail, setDetail] = useState<InstitutionDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

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

  if (selected) {
    const dnaOverlap = detail
      ? detail.trait_tags.filter((t) => t in careerDna).map(traitLabel)
      : [];

    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <button
          onClick={() => setSelected(null)}
          className="text-xs text-ink-faint hover:text-ink-muted"
        >
          ← Partner Colleges
        </button>

        <div className="mt-2 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-light text-ink">{selected.name}</h1>
            <p className="mt-1 text-sm text-ink-muted">{selected.city}, {selected.country}</p>
          </div>
          <Badge tone="warm">Collaborating Educational Organization</Badge>
        </div>

        {selected.id === "inst_niat" && (
          <p className="mt-3 text-xs italic leading-relaxed text-ink-faint">
            NIAT is seeded as Aureon's first collaborating educational organization and serves as
            the demonstration partner for the College Collaboration ecosystem.
          </p>
        )}

        {isLoadingDetail && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {detail && (
          <div className="mt-8 space-y-8">
            <section>
              <p className="text-sm leading-relaxed text-ink-muted">{detail.research_culture}</p>
            </section>

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
                <p className="text-xs uppercase tracking-widest text-ink-faint">Academic Programs</p>
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
              <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">
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
      <h1 className="text-2xl font-light text-ink">College Collaboration</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Aureon's collaborating educational organizations — real research labs, innovation centers,
        faculty, student ambassadors, and student projects, built on top of Institution
        Intelligence.
      </p>

      {partnerColleges.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Building2}
            title="No Collaborating Educational Organizations Yet"
            description="Aureon hasn't onboarded a partner college yet — check back once one has been added."
          />
        </div>
      ) : (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {partnerColleges.map((inst) => (
            <button key={inst.id} onClick={() => setSelected(inst)} className="text-left">
              <Surface tone="raised" padding="md" className="h-full transition hover:border-accent/40">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-ink">{inst.name}</p>
                  <Badge tone="warm">Partner</Badge>
                </div>
                <p className="mt-1 text-xs text-ink-faint">{inst.city}, {inst.country}</p>
                {inst.trait_tags.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
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

      {events.length > 0 && (
        <div className="mt-10">
          <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">Experience Events</p>
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
      <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">{title}</p>
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
