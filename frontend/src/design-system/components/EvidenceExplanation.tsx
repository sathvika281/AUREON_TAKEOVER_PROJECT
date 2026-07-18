/**
 * The shared "Explain Why" building block — Supporting -> Contradicting
 * -> Missing evidence, in that order, used everywhere a claim needs to
 * show its reasoning transparently (HypothesisCard, CandidateCard, and
 * every Phase 3 card: comparisons, mentor/college matches). Extracted
 * from what used to be near-identical duplicated JSX in HypothesisCard
 * and CandidateCard.
 */
export function EvidenceExplanation({
  supporting,
  contradicting,
  missing,
  markerClassName = "text-accent-soft",
}: {
  supporting: string[];
  contradicting: string[];
  missing: string[];
  /** Overrides the supporting-evidence "+" glyph color only — every
   * other color here stays the shared default. Used by screens with
   * their own local palette (e.g. Identity Discovery's indigo/gold). */
  markerClassName?: string;
}) {
  return (
    <>
      {supporting.length > 0 && (
        <div className="mt-3">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Supporting evidence</p>
          <ul className="mt-1.5 space-y-1">
            {supporting.map((item, i) => (
              <li key={i} className="text-xs text-ink-muted">
                <span className={markerClassName}>＋</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {contradicting.length > 0 && (
        <div className="mt-3">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Contradicting evidence</p>
          <ul className="mt-1.5 space-y-1">
            {contradicting.map((item, i) => (
              <li key={i} className="text-xs text-danger/85">
                <span>✕</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {missing.length > 0 && (
        <div className="mt-3">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Missing evidence</p>
          <ul className="mt-1.5 space-y-1">
            {missing.map((item, i) => (
              <li key={i} className="text-xs text-ink-faint">
                <span>–</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
