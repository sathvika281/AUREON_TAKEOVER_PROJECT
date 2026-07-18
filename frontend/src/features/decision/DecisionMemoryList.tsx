import { NotebookPen, Route, Scale, Star, X } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import type { DecisionMemoryActionType } from "../../shared/api/types";
import { relativeTime } from "../discovery/notebook/relativeTime";
import { useDecisionContext } from "./DecisionContext";

const ACTION_ICON: Record<DecisionMemoryActionType, typeof Scale> = {
  compared: Scale,
  shortlisted: Star,
  removed: X,
  simulated: Route,
};

const ACTION_LABEL: Record<DecisionMemoryActionType, string> = {
  compared: "Compared",
  shortlisted: "Shortlisted",
  removed: "Removed",
  simulated: "Simulated",
};

/**
 * The short, explained log of decision-relevant actions. Every reason
 * here was derived from data already computed elsewhere (never a fresh
 * LLM call) — see backend domain/services/decision_memory.py.
 */
export function DecisionMemoryList() {
  const { decisionMemory } = useDecisionContext();

  if (decisionMemory.length === 0) {
    return (
      <div className="mt-6">
        <EmptyStatePanel
          icon={NotebookPen}
          title="No Decisions Recorded Yet"
          description="Every time you compare careers, shortlist one, or remove one from consideration, the reason behind it is logged here automatically — a record of how you got to your decision, not just what it was."
        />
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-3">
      {decisionMemory.map((entry) => {
        const Icon = ACTION_ICON[entry.action_type];
        const subjects = Object.values(entry.career_names).join(" vs ");
        return (
          <Surface key={entry.id} tone="neutral" padding="md">
            <div className="flex items-center gap-2">
              <Icon className="h-4 w-4 text-accent-soft" />
              <p className="text-sm text-ink">
                {ACTION_LABEL[entry.action_type]} {subjects}
              </p>
            </div>
            <p className="mt-2 text-xs italic leading-relaxed text-ink-muted">Reason: {entry.reason}</p>
            <p className="mt-1.5 text-[0.68rem] text-ink-faint">{relativeTime(new Date(entry.created_at).getTime())}</p>
          </Surface>
        );
      })}
    </div>
  );
}
