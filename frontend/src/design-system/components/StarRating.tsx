import { Star } from "lucide-react";

import { cn } from "../cn";

/**
 * A compact 1-5 star row for a real, deterministic profile dimension —
 * never a ranking. Backed by `institution_profile.py`'s tier counts,
 * computed from real data (labs/centers/orgs/exchange programs), never
 * a fabricated or LLM-generated number.
 */
export function StarRating({ label, value, max = 5 }: { label: string; value: number; max?: number }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <p className="text-xs text-ink-muted">{label}</p>
      <div className="flex items-center gap-0.5" aria-label={`${label}: ${value} of ${max}`}>
        {Array.from({ length: max }, (_, i) => (
          <Star
            key={i}
            size={13}
            className={cn(i < value ? "fill-accent-soft text-accent-soft" : "text-border-strong")}
          />
        ))}
      </div>
    </div>
  );
}
