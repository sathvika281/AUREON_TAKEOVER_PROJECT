import { useCallback, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Compass, Heart, ShieldAlert } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { PageHeader } from "../../design-system/components/PageHeader";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import { apiClient } from "../../shared/api/client";
import type {
  CircleProgressResponse,
  CircleResourceProgress,
  KnowledgeCircleSummary,
  KnowledgeCircleView,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

/** One row per composed resource category in `KnowledgeCircleView` —
 * the `key` doubles as the `resource_type` sent to the bookmark/complete
 * endpoints, since the backend takes a freeform string, not a fixed enum. */
const RESOURCE_SECTIONS: { key: keyof KnowledgeCircleView; label: string }[] = [
  { key: "beginner_roadmap", label: "Beginner Roadmap" },
  { key: "beginner_projects", label: "Beginner Projects" },
  { key: "advanced_projects", label: "Advanced Projects" },
  { key: "books", label: "Books" },
  { key: "documentaries", label: "Documentaries" },
  { key: "podcasts", label: "Podcasts" },
  { key: "youtube_channels", label: "YouTube Channels" },
  { key: "journals_and_newsletters", label: "Journals & Newsletters" },
  { key: "conferences", label: "Conferences" },
  { key: "competitions", label: "Competitions" },
  { key: "hackathons", label: "Hackathons" },
  { key: "workshops", label: "Workshops" },
  { key: "communities", label: "Communities" },
  { key: "open_source_projects", label: "Open-Source Projects" },
  { key: "research_organizations", label: "Research Organizations" },
  { key: "laboratories", label: "Laboratories" },
  { key: "museums", label: "Museums" },
  { key: "startups", label: "Startups" },
  { key: "companies", label: "Companies" },
  { key: "universities", label: "Universities" },
  { key: "internships", label: "Internships" },
  { key: "certifications", label: "Certifications" },
  { key: "research_papers", label: "Research Papers" },
  { key: "government_initiatives", label: "Government Initiatives" },
  { key: "ngos", label: "NGOs" },
  { key: "volunteering_opportunities", label: "Volunteering Opportunities" },
  { key: "scholarships", label: "Scholarships" },
];

function progressKey(resourceType: string, resourceLabel: string): string {
  return `${resourceType}::${resourceLabel}`;
}

/**
 * Knowledge Circles — curated per-domain learning hubs, NOT a social
 * feed (no likes/followers/posts). Each circle is a real, composed
 * view merging its own authored content with the linked CareerWorld,
 * PassionResourceDomain(s), matching careers/trends/life missions —
 * every list here is real, never a placeholder. Students bookmark or
 * mark individual resources complete, building a real learning
 * checklist (`StudentProfile.circle_resource_progress`).
 */
export function KnowledgeCirclesScreen() {
  const studentId = getCurrentStudentId();

  const [circles, setCircles] = useState<KnowledgeCircleSummary[]>([]);
  // Loading, a genuine fetch failure, and a genuinely empty catalog are
  // three different product states — the original code had no loading
  // state at all for the list, so a fresh page load could briefly show
  // "No Circles Found" before real data arrived.
  const [listStatus, setListStatus] = useState<"loading" | "success" | "error">("loading");
  const [query, setQuery] = useState("");

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [view, setView] = useState<KnowledgeCircleView | null>(null);
  // The detail fetch must never leave the page blank on failure — idle
  // (nothing selected) is distinct from loading/success/error.
  const [viewStatus, setViewStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [progress, setProgress] = useState<CircleResourceProgress[]>([]);
  const [busyKey, setBusyKey] = useState<string | null>(null);

  const loadCircles = useCallback(() => {
    setListStatus("loading");
    apiClient
      .get<KnowledgeCircleSummary[]>("/v1/knowledge-circles")
      .then((r) => {
        setCircles(r);
        setListStatus("success");
      })
      .catch(() => setListStatus("error"));
  }, []);

  useEffect(() => {
    loadCircles();
  }, [loadCircles]);

  const loadView = useCallback(() => {
    if (!selectedId) return;
    setViewStatus("loading");
    apiClient
      .get<KnowledgeCircleView>(`/v1/knowledge-circles/${selectedId}`)
      .then((r) => {
        setView(r);
        setViewStatus("success");
      })
      .catch(() => setViewStatus("error"));
    apiClient
      .get<CircleProgressResponse>(`/v1/students/${studentId}/knowledge-circles/${selectedId}/progress`)
      .then((r) => setProgress(r.progress))
      .catch(() => {});
  }, [selectedId, studentId]);

  useEffect(() => {
    if (!selectedId) {
      setView(null);
      setProgress([]);
      setViewStatus("idle");
      return;
    }
    loadView();
  }, [selectedId, loadView]);

  const filteredCircles = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return circles;
    return circles.filter((c) => c.name.toLowerCase().includes(q) || c.overview.toLowerCase().includes(q));
  }, [circles, query]);

  const bookmarked = new Set(progress.filter((p) => p.status === "bookmarked").map((p) => progressKey(p.resource_type, p.resource_label)));
  const completed = new Set(progress.filter((p) => p.status === "completed").map((p) => progressKey(p.resource_type, p.resource_label)));

  async function toggleBookmark(resourceType: string, resourceLabel: string) {
    if (!selectedId) return;
    const key = progressKey(resourceType, resourceLabel);
    setBusyKey(key);
    try {
      const r = await apiClient.post<CircleProgressResponse>(
        `/v1/students/${studentId}/knowledge-circles/${selectedId}/bookmark`,
        { resource_type: resourceType, resource_label: resourceLabel },
      );
      setProgress(r.progress);
    } finally {
      setBusyKey(null);
    }
  }

  async function toggleComplete(resourceType: string, resourceLabel: string) {
    if (!selectedId) return;
    const key = progressKey(resourceType, resourceLabel);
    setBusyKey(key);
    try {
      const r = await apiClient.post<CircleProgressResponse>(
        `/v1/students/${studentId}/knowledge-circles/${selectedId}/complete`,
        { resource_type: resourceType, resource_label: resourceLabel },
      );
      setProgress(r.progress);
    } finally {
      setBusyKey(null);
    }
  }

  if (selectedId) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <button onClick={() => setSelectedId(null)} className="text-xs text-ink-faint hover:text-ink-muted">
          ← Knowledge Circles
        </button>

        {viewStatus === "loading" && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {viewStatus === "error" && (
          <div className="mt-6">
            <EmptyStatePanel
              icon={ShieldAlert}
              title="Couldn't Load This Circle"
              description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
              action={<Button variant="secondary" onClick={loadView}>Retry</Button>}
            />
          </div>
        )}

        {viewStatus === "success" && view && (
          <>
            <h1 className="mt-2 text-2xl font-light text-ink">{view.name}</h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">{view.overview}</p>
            {view.what_this_field_is_about && (
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{view.what_this_field_is_about}</p>
            )}

            {RESOURCE_SECTIONS.map(({ key, label }) => {
              const items = view[key] as string[];
              if (!items || items.length === 0) return null;
              return (
                <section key={key} className="mt-6">
                  <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{label}</p>
                  <div className="space-y-1.5">
                    {items.map((item, i) => {
                      const pk = progressKey(key, item);
                      const isBookmarked = bookmarked.has(pk);
                      const isCompleted = completed.has(pk);
                      const isBusy = busyKey === pk;
                      return (
                        <div key={i} className="flex items-center justify-between gap-3 rounded-lg px-1 py-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-ink-muted">{item}</span>
                            {isCompleted && <Badge tone="success">Completed</Badge>}
                          </div>
                          <div className="flex shrink-0 items-center gap-2">
                            <button
                              type="button"
                              disabled={isBusy}
                              aria-label={isBookmarked ? "Remove bookmark" : "Bookmark"}
                              onClick={() => toggleBookmark(key, item)}
                              className={cn("text-ink-faint transition hover:text-ink", isBookmarked && "text-accent-soft")}
                            >
                              <Heart size={15} className={cn(isBookmarked && "fill-current")} />
                            </button>
                            <button
                              type="button"
                              disabled={isBusy}
                              aria-label={isCompleted ? "Mark incomplete" : "Mark completed"}
                              onClick={() => toggleComplete(key, item)}
                              className={cn("text-ink-faint transition hover:text-ink", isCompleted && "text-success-soft")}
                            >
                              <CheckCircle2 size={15} className={cn(isCompleted && "fill-current")} />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <PageHeader
        title="Knowledge Circles"
        description="Curated, per-domain learning hubs — not a social feed. Books, projects, communities, competitions, research, and more, composed from Aureon's own real catalogs. Bookmark what's useful, mark what you've finished, and build a real learning checklist."
      />

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search a domain…"
        className="mt-6"
      />

      {listStatus === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : listStatus === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Knowledge Circles"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
            action={<Button variant="secondary" onClick={loadCircles}>Retry</Button>}
          />
        </div>
      ) : filteredCircles.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel icon={Compass} title="No Circles Found" description="Try a different search term." />
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {filteredCircles.map((circle) => (
            <button key={circle.id} onClick={() => setSelectedId(circle.id)} className="text-left">
              <Surface tone="raised" padding="md" className="flex h-full flex-col">
                <p className="text-sm font-medium text-ink">{circle.name}</p>
                <p className="mt-2 text-xs text-ink-muted">{circle.overview}</p>
              </Surface>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
