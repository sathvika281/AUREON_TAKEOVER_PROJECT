import { useEffect } from "react";
import { MessageSquarePlus } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import type { SuggestionRecord, SuggestionStatus } from "../../shared/api/types";
import { useSuggestionsContext } from "./SuggestionsContext";

const STATUS_TONE: Record<SuggestionStatus, "neutral" | "warm" | "success" | "cool" | "gold"> = {
  pending: "cool",
  under_review: "warm",
  needs_information: "warm",
  approved: "gold",
  implemented: "success",
  rejected: "neutral",
};

const STATUS_LABEL: Record<SuggestionStatus, string> = {
  pending: "Pending",
  under_review: "Under Review",
  needs_information: "Needs More Info",
  approved: "Approved",
  implemented: "Implemented",
  rejected: "Not This Time",
};

const CATEGORY_LABEL: Record<string, string> = {
  career: "Career Suggestion",
  opportunity: "Opportunity Suggestion",
  resource: "Resource Suggestion",
  feature_request: "Feature Request",
  correction: "Correction",
  general_feedback: "General Feedback",
};

function SuggestionCard({ suggestion }: { suggestion: SuggestionRecord }) {
  return (
    <Surface tone="raised" padding="md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-ink">{suggestion.title}</p>
          <p className="mt-1 text-xs text-ink-faint">{CATEGORY_LABEL[suggestion.category] ?? suggestion.category}</p>
        </div>
        <Badge tone={STATUS_TONE[suggestion.status]}>{STATUS_LABEL[suggestion.status]}</Badge>
      </div>
      <p className="mt-3 text-sm text-ink-muted">{suggestion.description}</p>
      {suggestion.review_notes && (
        <div className="mt-3 border-t border-border pt-3">
          <p className="text-xs text-ink-faint">Note from Aureon</p>
          <p className="mt-1 text-sm text-ink-muted">{suggestion.review_notes}</p>
        </div>
      )}
    </Surface>
  );
}

/**
 * The student's own submission history — reachable from the "Help Aureon
 * Grow" modal's confirmation step or by direct URL, deliberately not part
 * of `journeyConfig.ts`'s stage tree (same tier as `/profile`/`/history`).
 */
export function MySuggestionsScreen() {
  const { suggestions, isLoadingInitialData, ensureLoaded } = useSuggestionsContext();

  useEffect(() => {
    ensureLoaded();
  }, [ensureLoaded]);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">My Suggestions</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Everything you&rsquo;ve suggested to Aureon, and where it stands. Every submission is reviewed by a
        human before it becomes part of the platform.
      </p>

      {isLoadingInitialData ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : suggestions.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={MessageSquarePlus}
            title="No Suggestions Yet"
            description="Use “Help Aureon Grow” from the sidebar to suggest a missing career, report outdated information, or share feedback."
          />
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {suggestions.map((s) => (
            <SuggestionCard key={s.id} suggestion={s} />
          ))}
        </div>
      )}
    </div>
  );
}
