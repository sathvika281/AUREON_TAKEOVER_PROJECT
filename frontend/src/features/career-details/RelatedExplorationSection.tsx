import { Link } from "react-router-dom";

import { Surface } from "../../design-system/components/Surface";
import type { CareerSummary, TrendSummary } from "../../shared/api/types";

/**
 * "You might also find this interesting" — never a recommendation.
 * Related Careers/Recommended Next Exploration/Related Trends are all
 * real content adjacency, never a fit ranking.
 */
export function RelatedExplorationSection({
  relatedCareers,
  adjacentCareers,
  recommendedNextExploration,
  relatedTrends,
}: {
  relatedCareers: CareerSummary[];
  adjacentCareers: string[];
  recommendedNextExploration: CareerSummary | null;
  relatedTrends: TrendSummary[];
}) {
  if (relatedCareers.length === 0 && adjacentCareers.length === 0 && relatedTrends.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      {recommendedNextExploration && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Recommended next exploration</p>
          <Link
            to={`/explore/career-reality/${recommendedNextExploration.id}`}
            className="mt-1 block text-sm text-accent-soft hover:text-accent"
          >
            {recommendedNextExploration.name} →
          </Link>
        </div>
      )}
      {relatedCareers.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Related careers</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {relatedCareers.map((c) => (
              <Link
                key={c.id}
                to={`/explore/career-reality/${c.id}`}
                className="rounded-full border border-border px-2.5 py-1 text-xs text-ink-muted transition-colors hover:border-border-strong hover:text-ink"
              >
                {c.name}
              </Link>
            ))}
          </div>
        </div>
      )}
      {adjacentCareers.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Adjacent careers</p>
          <p className="mt-0.5 text-[0.7rem] text-ink-faint">Realistic transitions from this path, not same-field alternatives.</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {adjacentCareers.map((name) => (
              <span key={name} className="rounded-full border border-border px-2.5 py-1 text-xs text-ink-muted">
                {name}
              </span>
            ))}
          </div>
        </div>
      )}
      {relatedTrends.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Related trends</p>
          <div className="mt-1.5 space-y-1.5">
            {relatedTrends.map((t) => (
              <Link key={t.id} to="/explore/global-trends" className="block text-xs text-ink-muted hover:text-ink">
                {t.title}
              </Link>
            ))}
          </div>
        </div>
      )}
    </Surface>
  );
}
