import { motion } from "framer-motion";

import { EASE_CALM } from "../../../design-system/motion";

/**
 * The latest Aureon message shown prominently — "the question is right
 * in front of you" rather than "scroll to the bottom of a transcript."
 * Framed as an invitation to notice something, not "the AI's question."
 */
export function CurrentQuestion({ text }: { text: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: EASE_CALM }}
      className="px-4 text-center"
    >
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Notice what comes to mind</p>
      <p className="mt-2 text-lg font-light leading-relaxed text-ink">{text}</p>
    </motion.div>
  );
}
