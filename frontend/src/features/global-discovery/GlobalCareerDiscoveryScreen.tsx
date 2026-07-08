import { useEffect, useRef, useState } from "react";
import { Compass, SearchX } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { apiClient } from "../../shared/api/client";
import type { CareerSummary } from "../../shared/api/types";
import { CareerSummaryCard } from "./CareerSummaryCard";
import { CategoryFilter } from "./CategoryFilter";

/**
 * Global Career Discovery — an open catalog, not gated by evidence.
 * Students know only a tiny fraction of careers, so browsing itself needs
 * no personal profile; personalization only shows up once a career is
 * opened (see CareerDetailsScreen).
 */
export function GlobalCareerDiscoveryScreen() {
  const [careers, setCareers] = useState<CareerSummary[]>([]);
  const [category, setCategory] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Rapid filter/search changes can fire overlapping requests that resolve
  // out of order — only the response from the most recently *triggered*
  // request should ever be applied, or a slow earlier request can
  // overwrite a faster later one.
  const latestRequestId = useRef(0);

  useEffect(() => {
    const requestId = ++latestRequestId.current;
    setIsLoading(true);
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (query.trim()) params.set("q", query.trim());
    const qs = params.toString();
    apiClient
      .get<CareerSummary[]>(`/v1/careers${qs ? `?${qs}` : ""}`)
      .then((result) => {
        if (requestId === latestRequestId.current) setCareers(result);
      })
      .catch(() => {
        if (requestId === latestRequestId.current) setCareers([]);
      })
      .finally(() => {
        if (requestId === latestRequestId.current) setIsLoading(false);
      });
  }, [category, query]);

  const isFiltered = Boolean(category || query.trim());
  const sectionLabel = isFiltered ? "Search Results" : "All Careers";

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Career Reality</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Most students only know a handful of careers exist. Browse a wider, structured set —
        traditional, emerging, interdisciplinary, research, startup, government, non-profit, and
        country-specific — each with an honest look at what the work is actually like.
      </p>

      <div className="mt-6 space-y-4">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search careers…"
          className="w-full rounded-xl border border-border bg-surface px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/40 focus:outline-none"
        />
        <CategoryFilter selected={category} onSelect={setCategory} />
      </div>

      <div className="mt-8 flex items-center justify-between px-1">
        <p className="text-xs uppercase tracking-widest text-ink-faint">{sectionLabel}</p>
        {!isLoading && (
          <p className="text-xs text-ink-faint">
            {careers.length} career{careers.length === 1 ? "" : "s"}
          </p>
        )}
      </div>

      {isLoading ? (
        <p className="mt-4 text-sm text-ink-faint">Loading…</p>
      ) : careers.length === 0 ? (
        <div className="mt-4">
          <EmptyStatePanel
            icon={isFiltered ? SearchX : Compass}
            title={isFiltered ? "No Careers Match This Search" : "The Career Catalog Is Empty"}
            description={
              isFiltered
                ? "Try a different keyword, or clear the category filter to see the full catalog."
                : "Aureon's career catalog hasn't been populated yet — check back once it has."
            }
          />
        </div>
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          {careers.map((career) => (
            <CareerSummaryCard key={career.id} career={career} />
          ))}
        </div>
      )}
    </div>
  );
}
