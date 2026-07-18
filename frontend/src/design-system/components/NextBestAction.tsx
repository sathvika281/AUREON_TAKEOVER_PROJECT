import { Star } from "lucide-react";
import { Link } from "react-router-dom";

/**
 * One reusable suggestion, appearing on Your Universe, Career Explorer,
 * College Explorer, Expert Connect, and Decision Lab — never a
 * notification or popup, always at most one suggestion. Each screen
 * derives its own `NextBestActionSuggestion` from data it already has
 * (see each screen's local `deriveNextBestAction`); this component is
 * purely presentational and never decides what to suggest itself.
 */
export interface NextBestActionSuggestion {
  action: string;
  reason: string;
  to?: string;
}

export function NextBestAction({ suggestion }: { suggestion: NextBestActionSuggestion }) {
  const content = (
    <>
      <p className="flex items-center gap-1.5 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
        <Star size={11} className="fill-accent-soft" />
        Next Best Action
      </p>
      <p className="mt-1.5 text-sm font-medium text-ink">{suggestion.action}</p>
      <p className="mt-1 text-xs leading-relaxed text-ink-muted">{suggestion.reason}</p>
    </>
  );

  if (suggestion.to) {
    return (
      <Link
        to={suggestion.to}
        className="block rounded-xl border border-border p-4 transition-colors hover:border-accent-soft/40"
      >
        {content}
      </Link>
    );
  }

  return <div className="rounded-xl border border-border p-4">{content}</div>;
}
