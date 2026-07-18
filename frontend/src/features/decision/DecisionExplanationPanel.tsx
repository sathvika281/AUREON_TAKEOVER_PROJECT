import type { DecisionExplanation } from "../../shared/api/types";

/**
 * The traceable "why" behind a card's confidence — evidence grouped by
 * the real product surface it came from (Conversations, Reflection
 * Journal, Experience Lab, URL/Document/GitHub/Search Intelligence).
 * Same bullet/marker visual language as `EvidenceExplanation`, just
 * grouped by source instead of flattened, since the whole point here is
 * "which conversations/experiences/reflections contributed."
 */
export function DecisionExplanationPanel({ explanation }: { explanation: DecisionExplanation }) {
  const supportingEntries = Object.entries(explanation.supporting_by_source);
  const contradictingEntries = Object.entries(explanation.contradicting_by_source);

  if (supportingEntries.length === 0 && contradictingEntries.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-4">
      {supportingEntries.map(([source, items]) => (
        <div key={`supports-${source}`}>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">From {source}</p>
          <ul className="mt-1.5 space-y-1">
            {items.map((item, i) => (
              <li key={i} className="text-xs text-ink-muted">
                <span className="text-accent-soft">＋</span> {item}
              </li>
            ))}
          </ul>
        </div>
      ))}
      {contradictingEntries.map(([source, items]) => (
        <div key={`contradicts-${source}`}>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">From {source}</p>
          <ul className="mt-1.5 space-y-1">
            {items.map((item, i) => (
              <li key={i} className="text-xs text-danger/85">
                <span>✕</span> {item}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
