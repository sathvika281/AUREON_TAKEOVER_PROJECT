import { History } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { relativeTime } from "../discovery/notebook/relativeTime";
import { useDecisionContext } from "./DecisionContext";

const KIND_LABELS: Record<string, string> = {
  career_dna_change: "Career DNA",
  hypothesis_update: "Hypothesis",
  career_candidate: "Career Candidate",
  comparison: "Comparison",
  parallel_universe: "Parallel Universe",
};

/**
 * A visual history of how the decision has evolved — pure read of
 * already-persisted data (Discovery Notebook entries, comparisons,
 * simulations). Nothing here is fabricated; an empty profile shows an
 * honest empty state, not invented milestones.
 */
export function DecisionTimeline() {
  const { timelineMilestones, currentDirectionSummary, isTimelineLoading } = useDecisionContext();

  return (
    <div>
      <Surface tone="raised" padding="md">
        <p className="text-xs uppercase tracking-widest text-ink-faint">Current direction</p>
        <p className="mt-1 text-sm text-ink">{isTimelineLoading ? "Loading…" : currentDirectionSummary}</p>
      </Surface>

      {isTimelineLoading ? (
        <p className="mt-6 text-sm text-ink-faint">Loading…</p>
      ) : timelineMilestones.length === 0 ? (
        <div className="mt-6">
          <EmptyStatePanel
            icon={History}
            title="Your Timeline Is Still Empty"
            description="This fills in automatically as Career DNA changes, hypotheses update, and you compare or simulate careers in Decision Lab — a record of how your direction evolved, not a manual log."
          />
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {timelineMilestones.map((m, i) => (
            <div key={i} className="flex gap-3 border-l-2 border-border pl-3">
              <div>
                <p className="text-[0.65rem] uppercase tracking-widest text-accent-soft">
                  {KIND_LABELS[m.kind] ?? m.kind}
                </p>
                <p className="mt-1 text-sm text-ink-muted">{m.text}</p>
                <p className="mt-1 text-[0.68rem] text-ink-faint">{relativeTime(new Date(m.created_at).getTime())}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
