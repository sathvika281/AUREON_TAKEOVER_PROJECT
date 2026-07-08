import { AnimatePresence, motion } from "framer-motion";
import { useEffect } from "react";

import { EASE_CALM } from "../../../design-system/motion";

const HOLD_MS = 3200;

/**
 * Generalizes the original "first hypothesis" reveal into a reusable
 * moment with two real, honestly-derived triggers (see DiscoveryContext):
 * the first hypothesis forming, and the first Hidden Potential pattern
 * being found. Unlike every other animation in the product, this is the
 * one place motion *decreases* — the backdrop stills everything behind it
 * and a single quiet line holds, rather than another effect layering on
 * top. No confetti, no "achievement" framing.
 */
export function InsightMoment({
  line,
  onComplete,
}: {
  line: string | null;
  onComplete: () => void;
}) {
  useEffect(() => {
    if (!line) return;
    const timer = setTimeout(onComplete, HOLD_MS);
    return () => clearTimeout(timer);
  }, [line, onComplete]);

  return (
    <AnimatePresence>
      {line && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.2, ease: EASE_CALM }}
          className="fixed inset-0 z-40 flex items-center justify-center bg-canvas/90"
        >
          <motion.p
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 1.6, ease: EASE_CALM, delay: 0.3 }}
            className="max-w-md px-8 text-center text-xl font-light leading-relaxed text-ink"
          >
            {line}
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
