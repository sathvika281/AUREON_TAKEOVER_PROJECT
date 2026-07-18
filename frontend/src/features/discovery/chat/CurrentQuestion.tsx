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
      className="px-4"
    >
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-[#6E6A5E]">
        Notice what comes to mind
      </p>
      <p className="mt-2 font-serif text-lg leading-relaxed text-[#F2EDE0]">{text}</p>
    </motion.div>
  );
}
