import { motion } from "framer-motion";
import { forwardRef } from "react";

import { EvidenceExplanation } from "../../../design-system/components/EvidenceExplanation";
import { Surface } from "../../../design-system/components/Surface";
import { EASE_CALM } from "../../../design-system/motion";
import type { CareerHypothesis } from "../../../shared/api/types";

const STATUS_LABEL: Record<string, string> = {
  investigating: "Investigating",
  growing: "Growing",
  strong: "Strong",
  validated: "Validated",
  discarded: "Discarded",
};

/**
 * Evidence-first, always. Order here is: Supporting Evidence ->
 * Contradicting Evidence -> Missing Evidence -> Current Conflict
 * (synthesized tension) -> Evidence Strength (the deterministic
 * lifecycle status — never LLM-self-reported) -> Working Hypothesis (the
 * tentative name, last, as a working label rather than a headline).
 *
 * Forwards its ref to the outer motion.div — AnimatePresence's
 * `mode="popLayout"` needs to attach a ref to measure exiting elements.
 */
export const HypothesisCard = forwardRef<
  HTMLDivElement,
  { hypothesis: CareerHypothesis }
>(function HypothesisCard({ hypothesis }, ref) {
  const conflict =
    hypothesis.supporting_evidence[0] && hypothesis.missing_evidence[0]
      ? `While ${hypothesis.supporting_evidence[0]} suggests interest, ${hypothesis.missing_evidence[0]} is still unclear.`
      : null;

  return (
    <motion.div
      ref={ref}
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.6, ease: EASE_CALM }}
    >
      <Surface tone="raised" padding="md">
        <EvidenceExplanation
          supporting={hypothesis.supporting_evidence}
          contradicting={hypothesis.contradicting_evidence}
          missing={hypothesis.missing_evidence}
        />

        {conflict && (
          <p className="mt-3 border-l border-border-strong pl-3 text-xs italic leading-relaxed text-ink-muted">
            {conflict}
          </p>
        )}

        <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
          <span className="font-mono text-xs text-accent-soft">
            {STATUS_LABEL[hypothesis.status] ?? hypothesis.status}
          </span>
          <span className="text-right text-xs text-ink-faint">
            Working hypothesis: <span className="text-ink">{hypothesis.career_name}</span>
          </span>
        </div>
        {hypothesis.transition_reason && (
          <p className="mt-1.5 text-[0.68rem] text-ink-faint">{hypothesis.transition_reason}</p>
        )}
      </Surface>
    </motion.div>
  );
});
