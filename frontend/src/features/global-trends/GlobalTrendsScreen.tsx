import { useCallback, useEffect, useState } from "react";
import { LineChart, ShieldAlert } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { FilterPill } from "../../design-system/components/FilterPill";
import { PageHeader } from "../../design-system/components/PageHeader";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { FutureSkillsResponse, Trend, TrendsResponse } from "../../shared/api/types";

const CATEGORY_LABELS: Record<string, string> = {
  emerging_industry: "Emerging Industry",
  declining_industry: "Declining Industry",
  future_technology: "Future Technology",
  skill_shift: "Skill Shift",
  hiring_shift: "Hiring Shift",
  ai_influence: "AI Influence",
  research_direction: "Research Direction",
};

const TIME_HORIZON_LABELS: Record<string, string> = {
  near_term: "Near-term",
  mid_term: "Mid-term",
  long_term: "Long-term",
};

/**
 * Global Trends — industry/market-level growth patterns, deliberately
 * distinct from any single career's own Future Outlook narrative. Never
 * a career recommendation — only real, honestly-labeled exposure to
 * what's shifting in the world.
 */
export function GlobalTrendsScreen() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [futureSkills, setFutureSkills] = useState<FutureSkillsResponse["skills"]>([]);
  const [category, setCategory] = useState<string | null>(null);
  // Loading, a genuine fetch failure, and a genuinely empty catalog for
  // this category are three different product states.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    // Additive, non-primary section — degrades honestly on failure by
    // simply not rendering (see its own `length > 0` guard below), same
    // discipline as JourneyStoriesScreen's filters/relevant-stories.
    void apiClient.get<FutureSkillsResponse>("/v1/trends/future-skills").then((r) => setFutureSkills(r.skills));
  }, []);

  const loadTrends = useCallback(() => {
    setStatus("loading");
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    const qs = params.toString();
    apiClient
      .get<TrendsResponse>(`/v1/trends${qs ? `?${qs}` : ""}`)
      .then((r) => {
        setTrends(r.trends);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [category]);

  useEffect(() => {
    loadTrends();
  }, [loadTrends]);

  const categories = Object.keys(CATEGORY_LABELS);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <PageHeader
        title="Global Trends"
        description="What possibilities exist in the world right now — real, honestly-labeled industry and market shifts, never a career recommendation."
      />

      {futureSkills.length > 0 && (
        <div className="mt-6">
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            Skills Named Across the Most Trends
          </p>
          <div className="flex flex-wrap gap-1.5">
            {futureSkills.slice(0, 12).map((s) => (
              <Badge key={s.skill} tone="cool">
                {s.skill} · {s.mentioned_in_trend_count}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8">
        <div className="flex flex-wrap gap-1.5">
          <FilterPill active={category === null} onClick={() => setCategory(null)}>
            All
          </FilterPill>
          {categories.map((c) => (
            <FilterPill key={c} active={category === c} onClick={() => setCategory(c)}>
              {CATEGORY_LABELS[c]}
            </FilterPill>
          ))}
        </div>

        {status === "loading" ? (
          <p className="mt-6 text-sm text-ink-faint">Loading…</p>
        ) : status === "error" ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={ShieldAlert}
              title="Couldn't Load Global Trends"
              description="Something went wrong reaching Aureon's servers — this isn't the same as there being no trends. Try again."
              action={<Button variant="secondary" onClick={loadTrends}>Retry</Button>}
            />
          </div>
        ) : trends.length === 0 ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={LineChart}
              title="No Trends Here Yet"
              description="Aureon's Global Trends knowledge base hasn't been populated for this category yet."
            />
          </div>
        ) : (
          <div className="mt-6 space-y-4">
            {trends.map((trend) => (
              <Surface key={trend.id} tone="raised" padding="lg">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-ink">{trend.title}</p>
                    <p className="mt-1 text-sm leading-relaxed text-ink-muted">{trend.summary}</p>
                  </div>
                  <Badge tone="neutral">{TIME_HORIZON_LABELS[trend.time_horizon]}</Badge>
                </div>
                <p className="mt-3 text-sm leading-relaxed text-ink-muted">{trend.description}</p>
                {trend.affected_industries.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {trend.affected_industries.map((i) => (
                      <Badge key={i} tone="cool">{i}</Badge>
                    ))}
                  </div>
                )}

                {trend.key_milestones.length > 0 && (
                  <div className="mt-4">
                    <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Timeline</p>
                    <ul className="mt-1.5 space-y-1">
                      {trend.key_milestones.map((m) => (
                        <li key={m} className="text-xs leading-relaxed text-ink-muted">{m}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {(trend.countries_leading.length > 0 || trend.affected_careers.length > 0) && (
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    {trend.countries_leading.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Countries Leading</p>
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {trend.countries_leading.map((c) => (
                            <Badge key={c} tone="neutral">{c}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {trend.affected_careers.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Affected Careers</p>
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {trend.affected_careers.map((c) => (
                            <Badge key={c} tone="neutral">{c}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {(trend.companies.length > 0 || trend.startups.length > 0) && (
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    {trend.companies.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Companies</p>
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {trend.companies.map((c) => (
                            <Badge key={c} tone="cool">{c}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {trend.startups.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Startups</p>
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {trend.startups.map((s) => (
                            <Badge key={s} tone="cool">{s}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {trend.government_initiatives.length > 0 && (
                  <div className="mt-4">
                    <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Government Initiatives</p>
                    <ul className="mt-1.5 space-y-1">
                      {trend.government_initiatives.map((g) => (
                        <li key={g} className="text-xs leading-relaxed text-ink-muted">{g}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {(trend.risks.length > 0 || trend.opportunities.length > 0) && (
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    {trend.risks.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Risks</p>
                        <ul className="mt-1.5 space-y-1">
                          {trend.risks.map((r) => (
                            <li key={r} className="text-xs leading-relaxed text-ink-muted">{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {trend.opportunities.length > 0 && (
                      <div>
                        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Opportunities</p>
                        <ul className="mt-1.5 space-y-1">
                          {trend.opportunities.map((o) => (
                            <li key={o} className="text-xs leading-relaxed text-ink-muted">{o}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {trend.research_papers.length > 0 && (
                  <div className="mt-4">
                    <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Research Directions</p>
                    <ul className="mt-1.5 space-y-1">
                      {trend.research_papers.map((p) => (
                        <li key={p} className="text-xs leading-relaxed text-ink-muted">{p}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <p className="mt-4 text-[0.65rem] text-ink-faint">{trend.source_note}</p>
              </Surface>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
