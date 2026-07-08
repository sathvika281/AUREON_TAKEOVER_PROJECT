import { RefreshCw } from "lucide-react";

import type { NotebookEntry } from "../../../shared/api/types";
import { relativeTime } from "./relativeTime";

/**
 * Distinct from a plain ObservationEntry — this documents Aureon
 * changing its mind, and now renders the real four-part story the
 * backend records: what it believed before, the new evidence that
 * arrived, what it believes now, and why — not a single flattened
 * sentence.
 */
export function BeliefRevisionEntry({ entry }: { entry: NotebookEntry }) {
  const hasStructuredStory = entry.previous_state && entry.updated_belief;

  return (
    <div className="border-l border-accent/30 py-2.5 pl-4">
      <div className="flex items-start gap-2">
        <RefreshCw size={13} className="mt-0.5 shrink-0 text-accent-soft" />
        <p className="text-sm leading-relaxed text-ink">{entry.text}</p>
      </div>

      {hasStructuredStory && (
        <div className="mt-2 space-y-1 pl-5 text-xs text-ink-muted">
          <p>
            <span className="text-ink-faint">Believed:</span> {entry.previous_state}
          </p>
          {entry.new_evidence && (
            <p>
              <span className="text-ink-faint">New evidence:</span> {entry.new_evidence}
            </p>
          )}
          <p>
            <span className="text-ink-faint">Now:</span> {entry.updated_belief}
          </p>
          {entry.reason && (
            <p className="italic text-ink-faint">because {entry.reason}</p>
          )}
        </div>
      )}

      <p className="mt-1.5 pl-5 text-[0.68rem] text-ink-faint">
        {relativeTime(new Date(entry.created_at).getTime())}
      </p>
    </div>
  );
}
