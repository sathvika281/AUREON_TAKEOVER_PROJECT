import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { Surface } from "./Surface";
import type { MissionEvidence } from "../../shared/api/types";

/**
 * Aureon's one universal evidence viewer — every specialist's evidence
 * (Browser/PDF/Resume/GitHub/Institution/Mentor/Opportunity Intelligence
 * alike) renders through this exact component, never a per-source
 * redesign. Collapsed: title, source, confidence. Expanded: summary,
 * metadata, timestamp, related artifact if the evidence names one.
 */
export function EvidenceCard({ evidence }: { evidence: MissionEvidence }) {
  const [expanded, setExpanded] = useState(false);
  const metadataEntries = Object.entries(evidence.metadata ?? {});
  const relatedArtifact = evidence.metadata?.["category"] as string | undefined;

  return (
    <Surface tone="neutral" padding="md">
      <button
        onClick={() => setExpanded((prev) => !prev)}
        className="flex w-full items-start justify-between gap-3 text-left"
      >
        <div>
          <p className="text-sm font-medium text-ink">{evidence.title ?? evidence.source}</p>
          <p className="mt-0.5 text-xs text-ink-faint">{evidence.source}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {evidence.confidence !== null && (
            <span className="font-mono text-xs tracking-wide text-accent-soft">
              {Math.round(evidence.confidence * 100)}%
            </span>
          )}
          {expanded ? <ChevronUp size={14} className="text-ink-faint" /> : <ChevronDown size={14} className="text-ink-faint" />}
        </div>
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-border pt-3">
          <p className="text-sm leading-relaxed text-ink-muted">{evidence.summary}</p>
          {relatedArtifact && (
            <p className="text-xs text-ink-faint">
              <span className="text-ink-faint">Related: </span>{relatedArtifact}
            </p>
          )}
          {metadataEntries.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {metadataEntries
                .filter(([key]) => key !== "category")
                .map(([key, value]) => (
                  <span key={key} className="rounded-full border border-border px-2 py-0.5 font-mono text-[0.65rem] text-ink-faint">
                    {key}: {String(Array.isArray(value) ? value.join(", ") : value)}
                  </span>
                ))}
            </div>
          )}
          <p className="font-mono text-[0.65rem] tracking-wide text-ink-faint">
            {new Date(evidence.timestamp).toLocaleString()}
          </p>
        </div>
      )}
    </Surface>
  );
}
