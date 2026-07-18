import { motion } from "framer-motion";

import { EASE_CALM } from "../../../design-system/motion";

/**
 * Shown only before the very first message — the first thing a student
 * (or a judge) reads should frame exploration, not "tell me about
 * yourself." Retires permanently the moment messages.length > 0.
 */
export function UniverseIntro() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 1, ease: EASE_CALM }}
      className="max-w-sm"
    >
      <p className="font-serif text-base italic leading-relaxed text-[#9C978A]">
        Every student has a unique universe.
      </p>
      <p className="mt-2 font-serif text-base italic leading-relaxed text-[#9C978A]">
        Aureon doesn't choose your future. It gradually understands it.
      </p>
      <p className="mt-4 text-sm font-medium leading-relaxed text-[#F2EDE0]">Let's begin discovering yours.</p>
    </motion.div>
  );
}
