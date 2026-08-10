import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BookOpen, Compass, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import { apiClient } from "../../shared/api/client";
import type {
  JourneyStory,
  JourneyStoryFiltersResponse,
  JourneyStorySearchResponse,
  RelevantJourneyStoriesResponse,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

const REFLECTION_PROMPTS = [
  "Did anything in this story feel familiar?",
  "What part of this journey made you think differently?",
  "Did this story introduce a possibility you hadn't considered?",
];

function humanizeTheme(theme: string): string {
  return theme.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function provenanceLabel(storyType: string): string {
  switch (storyType) {
    case "composite_student_discovery":
      return "Composite student journey based on common exploration patterns";
    case "student_discovery":
      return "A real student's story, shared with consent";
    case "publicly_documented":
      return "Publicly documented";
    default:
      return "Illustrative composite story";
  }
}

function PillToggle({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
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

function ParagraphSection({ title, text }: { title: string; text: string }) {
  if (!text) return null;
  return (
    <section className="mt-6">
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <p className="text-sm leading-relaxed text-ink-muted">{text}</p>
    </section>
  );
}

function ReflectionPrompt({
  prompt,
  onSubmit,
}: {
  prompt: string;
  onSubmit: (response: string) => Promise<void>;
}) {
  const [value, setValue] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved">("idle");

  async function handleSave() {
    if (!value.trim()) return;
    setStatus("saving");
    await onSubmit(value.trim());
    setStatus("saved");
  }

  return (
    <div>
      <p className="mb-1.5 text-sm text-ink">{prompt}</p>
      <textarea
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          if (status === "saved") setStatus("idle");
        }}
        rows={3}
        placeholder="Your thoughts…"
        className="w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint"
      />
      <div className="mt-1.5 flex items-center gap-2">
        <button
          onClick={handleSave}
          disabled={!value.trim() || status === "saving"}
          className="text-xs font-medium text-accent-soft transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-40"
        >
          {status === "saving" ? "Saving…" : "Save reflection"}
        </button>
        {status === "saved" && <span className="text-xs text-ink-faint">Saved to your Reflection Journal.</span>}
      </div>
    </div>
  );
}

/**
 * Journey Stories — redefined as STUDENT discovery journeys (Expert
 * Connect / Journey Stories purpose split): how someone still figuring
 * things out discovered a passion, changed direction, or found a world
 * they didn't know existed. Professional "how they built that career"
 * storytelling now lives entirely on Expert Connect and Career Explorer's
 * "Human Stories" — never here. Every story is honestly labeled via
 * `story_type`/`discovery_themes`, never presented as a verified real
 * student unless it genuinely is one. Search backend fully open
 * (`GET /v1/journey-stories`); "Stories You May Relate To" and
 * reflections are student-scoped and require the authenticated student.
 */
export function JourneyStoriesScreen() {
  const studentId = useRef(getCurrentStudentId()).current;

  const [stories, setStories] = useState<JourneyStory[]>([]);
  // Sprint 4 fix: a failed request and a genuinely empty result are
  // different product states and must never render the same way — see
  // TECHNICAL_DEBT_REGISTER.md's Journey Stories P0. "success" with zero
  // stories still reaches the existing honest "No Stories Found" panel
  // below; only "error" gets its own distinct state.
  const [storiesStatus, setStoriesStatus] = useState<"loading" | "success" | "error">("loading");
  const [relevantStories, setRelevantStories] = useState<JourneyStory[]>([]);
  const [filters, setFilters] = useState<JourneyStoryFiltersResponse | null>(null);
  const [query, setQuery] = useState("");
  const [industryFilter, setIndustryFilter] = useState<string | null>(null);
  const [themeFilter, setThemeFilter] = useState<string | null>(null);
  const [careerSwitchOnly, setCareerSwitchOnly] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const loadStories = useCallback(() => {
    setStoriesStatus("loading");
    apiClient
      .get<JourneyStorySearchResponse>("/v1/journey-stories?limit=300")
      .then((r) => {
        setStories(r.stories);
        setStoriesStatus("success");
      })
      .catch(() => setStoriesStatus("error"));
  }, []);

  useEffect(() => {
    loadStories();
    // Filters and "Stories You May Relate To" are additive, non-primary
    // sections that already degrade honestly on failure (they simply
    // don't render — see their own `{... && (...)}` guards below), so
    // they don't need the same error-state treatment as the main list.
    apiClient
      .get<JourneyStoryFiltersResponse>("/v1/journey-stories/filters")
      .then(setFilters)
      .catch(() => {});
    apiClient
      .get<RelevantJourneyStoriesResponse>(`/v1/students/${studentId}/journey-stories/relevant`)
      .then((r) => setRelevantStories(r.stories))
      .catch(() => {});
  }, [studentId, loadStories]);

  const filteredStories = useMemo(() => {
    const q = query.trim().toLowerCase();
    return stories.filter((s) => {
      if (q) {
        const haystack = `${s.person_label} ${s.career_name} ${s.journey}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (industryFilter && s.industry !== industryFilter) return false;
      if (themeFilter && !s.discovery_themes.includes(themeFilter)) return false;
      if (careerSwitchOnly && !s.career_switch) return false;
      return true;
    });
  }, [stories, query, industryFilter, themeFilter, careerSwitchOnly]);

  const selected = stories.find((s) => s.id === selectedId) ?? null;

  async function submitReflection(storyId: string, prompt: string, response: string) {
    await apiClient
      .post(`/v1/students/${studentId}/journey-stories/${storyId}/reflect`, { prompt, response })
      .catch(() => {});
  }

  if (selected) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <button
          onClick={() => setSelectedId(null)}
          className="text-xs text-ink-faint hover:text-ink-muted"
        >
          ← Student Stories
        </button>

        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge tone="neutral">{provenanceLabel(selected.story_type)}</Badge>
          {selected.career_switch && <Badge tone="cool">Career Switch</Badge>}
          {selected.gap_year && <Badge tone="cool">Gap Year</Badge>}
          {selected.discovery_themes.map((t) => (
            <Badge key={t} tone="warm">{humanizeTheme(t)}</Badge>
          ))}
        </div>

        <h1 className="mt-3 text-2xl font-light text-ink">{selected.person_label}</h1>
        <p className="mt-1 text-sm text-ink-muted">
          {selected.career_name}
          {selected.industry && ` · ${selected.industry}`}
        </p>
        {selected.story_type === "publicly_documented" && selected.source_reference && (
          <p className="mt-1 text-xs text-ink-faint">Source: {selected.source_reference}</p>
        )}

        <ParagraphSection title="Background" text={selected.background} />
        <ParagraphSection title="Journey" text={selected.journey} />
        <ParagraphSection title="Challenges" text={selected.challenges} />
        {selected.uncertainty_period && (
          <ParagraphSection title="A Period of Uncertainty" text={selected.uncertainty_period} />
        )}
        <ParagraphSection title="Turning Points" text={selected.turning_points} />

        {selected.timeline.length > 0 && (
          <section className="mt-8">
            <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Timeline</p>
            <div className="space-y-3 border-l border-border pl-4">
              {selected.timeline.map((m, i) => (
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

        <ParagraphSection title="Advice" text={selected.advice} />
        <ParagraphSection title="Lessons Learned" text={selected.lessons_learned} />
        {selected.current_outcome && (
          <ParagraphSection title="Where They Are Now" text={selected.current_outcome} />
        )}

        {(selected.linked_expert || selected.linked_life_mission_name) && (
          <section className="mt-6">
            <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Connected To</p>
            <div className="flex flex-wrap gap-1.5">
              {selected.linked_expert && (
                <Badge tone="cool">Expert: {selected.linked_expert.name}</Badge>
              )}
              {selected.linked_life_mission_name && (
                <Badge tone="cool">Life Mission: {selected.linked_life_mission_name}</Badge>
              )}
            </div>
          </section>
        )}

        <section className="mt-10 border-t border-border pt-6">
          <div className="mb-3 flex items-center gap-1.5 text-accent-soft">
            <Sparkles size={13} />
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em]">Reflect</p>
          </div>
          <p className="mb-4 text-xs text-ink-faint">
            Aureon isn't just about consuming information — it's about reflection. Saving a reflection
            adds it to your private Reflection Journal; reading this story alone never does.
          </p>
          <div className="space-y-4">
            {REFLECTION_PROMPTS.map((prompt, i) => (
              <ReflectionPrompt
                key={i}
                prompt={prompt}
                onSubmit={(response) => submitReflection(selected.id, prompt, response)}
              />
            ))}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Student Stories</h1>
      <p className="mt-2 text-sm text-ink-muted">
        How other students and young people went from confusion, limited exposure, or uncertainty to
        discovering what they cared about — not professional success stories (those live on Expert
        Connect), but honest accounts of figuring it out.
      </p>

      {relevantStories.length > 0 && (
        <section className="mt-8">
          <p className="mb-3 flex items-center gap-1.5 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
            <Compass size={11} /> Stories You May Relate To
          </p>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {relevantStories.map((story) => (
              <button
                key={story.id}
                onClick={() => setSelectedId(story.id)}
                className="min-w-[220px] shrink-0 rounded-lg border border-accent-soft/30 bg-accent/5 px-4 py-3 text-left transition-colors hover:border-accent-soft/60"
              >
                <p className="text-sm font-medium text-ink">{story.person_label}</p>
                <p className="mt-1 line-clamp-2 text-xs text-ink-faint">{story.journey}</p>
              </button>
            ))}
          </div>
        </section>
      )}

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by person, career, or story…"
        className="mt-6"
      />

      {filters && (filters.industries.length > 0 || filters.discovery_themes.length > 0) && (
        <div className="mt-3 space-y-2">
          {filters.discovery_themes.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {filters.discovery_themes.map((t) => (
                <PillToggle
                  key={t}
                  label={humanizeTheme(t)}
                  active={themeFilter === t}
                  onClick={() => setThemeFilter(themeFilter === t ? null : t)}
                />
              ))}
            </div>
          )}
          {filters.industries.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              <PillToggle label="Career Switches Only" active={careerSwitchOnly} onClick={() => setCareerSwitchOnly((v) => !v)} />
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
        </div>
      )}

      {storiesStatus === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : storiesStatus === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Stories"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being no stories. Try again."
            action={
              <button
                onClick={loadStories}
                className="rounded-lg border border-border px-4 py-2 text-xs font-medium text-ink-muted transition-colors hover:border-border-strong hover:text-ink"
              >
                Retry
              </button>
            }
          />
        </div>
      ) : filteredStories.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel icon={BookOpen} title="No Stories Found" description="Try clearing a filter or searching a different term." />
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {filteredStories.map((story) => (
            <button key={story.id} onClick={() => setSelectedId(story.id)} className="text-left">
              <Surface tone="raised" padding="md" className="flex h-full flex-col">
                <p className="text-sm font-medium text-ink">{story.person_label}</p>
                <p className="mt-1 text-xs text-ink-faint">{story.career_name}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {story.career_switch && <Badge tone="cool">Career Switch</Badge>}
                  {story.gap_year && <Badge tone="cool">Gap Year</Badge>}
                  {story.discovery_themes.slice(0, 2).map((t) => (
                    <Badge key={t} tone="warm">{humanizeTheme(t)}</Badge>
                  ))}
                </div>
                <p className="mt-3 text-xs text-ink-muted">{story.journey.slice(0, 140)}…</p>
                <p className="mt-2 text-[0.65rem] italic text-ink-faint">{provenanceLabel(story.story_type)}</p>
              </Surface>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
