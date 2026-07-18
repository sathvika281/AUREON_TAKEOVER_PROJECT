import { useEffect, useRef, useState } from "react";
import { Compass, SearchX } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { NextBestAction, type NextBestActionSuggestion } from "../../design-system/components/NextBestAction";
import { apiClient } from "../../shared/api/client";
import type { CareerCandidate, CareerSummary } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";
import { CandidateCard } from "../career-intelligence/CandidateCard";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { CareerSummaryCard } from "./CareerSummaryCard";
import { CategoryFilter } from "./CategoryFilter";

function deriveNextBestAction(candidates: CareerCandidate[]): NextBestActionSuggestion {
  const notShortlisted = candidates.find((c) => !c.is_shortlisted);
  if (notShortlisted) {
    return {
      action: `Explore ${notShortlisted.career_name}`,
      reason: notShortlisted.supporting_evidence[0] ?? notShortlisted.why_it_matches,
      to: `/explore/career-reality/${notShortlisted.career_id}`,
    };
  }
  return {
    action: "Analyze your fit",
    reason: "See real careers reasoned against your Career DNA — no career here is ever a guess.",
  };
}

/**
 * Career Explorer — what careers fit me? Leads with real, personalized
 * matches (merged in from the old standalone Career Intelligence
 * screen), then the full open catalog below — never gated behind
 * evidence, since students know only a tiny fraction of careers exist.
 * Deeper personalization (Career Reality, Future Outlook, per-career
 * match evidence) lives on CareerDetailsScreen.
 */
export function GlobalCareerDiscoveryScreen() {
  const { notebookEntries } = useDiscoveryContext();
  const {
    candidates, insufficientEvidence, insufficientEvidenceReason, isAnalyzing, error,
    hasAnalyzedOnce, analyzeCareers, shortlistCandidate, removeCandidate,
  } = useCareerIntelligenceContext();

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
    // Reorders the catalog by real World Signal alignment — never
    // filters; every career the filters/search matched is still returned.
    params.set("student_id", getCurrentStudentId());
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
      <h1 className="text-2xl font-light text-ink">Career Explorer</h1>
      <p className="mt-2 text-sm text-ink-muted">
        What careers fit me? Real, personalized matches first — then a wider, structured catalog
        to browse on your own.
      </p>

      {candidates.length > 0 && (
        <div className="mt-6">
          <NextBestAction suggestion={deriveNextBestAction(candidates)} />
        </div>
      )}

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Recommended For You</p>
          <Button size="md" onClick={analyzeCareers} disabled={isAnalyzing}>
            {isAnalyzing ? "Analyzing…" : hasAnalyzedOnce ? "Re-analyze My Fit" : "Analyze My Fit"}
          </Button>
        </div>
        {error && <p className="mt-2 text-xs text-danger">{error}</p>}

        {insufficientEvidence ? (
          <div className="mt-3">
            <EmptyStatePanel
              icon={Compass}
              title="Not Enough Evidence Yet"
              description={
                insufficientEvidenceReason ??
                "Aureon needs more evidence in your Career DNA before it can reason about career fit responsibly."
              }
            />
          </div>
        ) : candidates.length === 0 ? (
          <div className="mt-3">
            <EmptyStatePanel
              icon={Compass}
              title="No Matches Yet"
              description="Analyze your fit above to see real careers reasoned from your current Career DNA — based on your real conversations and evidence so far."
            />
          </div>
        ) : (
          <div className="mt-3 space-y-3">
            <p className="text-[0.65rem] text-ink-faint">Based on {notebookEntries.length} real conversations and evidence entries.</p>
            {candidates.map((candidate) => (
              <CandidateCard
                key={candidate.career_id}
                candidate={candidate}
                onShortlist={shortlistCandidate}
                onRemove={removeCandidate}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-10">
        <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
          Explore All Careers
        </p>
        <div className="space-y-4">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search careers…"
          />
          <CategoryFilter selected={category} onSelect={setCategory} />
        </div>

        <div className="mt-6 flex items-center justify-between px-1">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{sectionLabel}</p>
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
    </div>
  );
}
