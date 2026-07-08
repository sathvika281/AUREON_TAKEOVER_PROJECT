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
}: {
  supporting: string[];
  contradicting: string[];
  missing: string[];
}) {
  return (
    <>
      {supporting.length > 0 && (
        <div className="mt-3">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Supporting evidence</p>
          <ul className="mt-1.5 space-y-1">
            {supporting.map((item, i) => (
              <li key={i} className="text-xs text-ink-muted">
                <span className="text-accent-soft">＋</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {contradicting.length > 0 && (
        <div className="mt-3">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Contradicting evidence</p>
          <ul className="mt-1.5 space-y-1">
            {contradicting.map((item, i) => (
              <li key={i} className="text-xs text-red-300/80">
                <span>✕</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {missing.length > 0 && (
        <div className="mt-3">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Missing evidence</p>
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
