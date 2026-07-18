import { motion } from "framer-motion";

import { Logo } from "../../../design-system/components/Logo";
import { EASE_CALM } from "../../../design-system/motion";
import { decorativeStars } from "./layoutUniverse";

const stars = decorativeStars();

/**
 * Shown once, ever, the first time a student reaches Your Universe with
 * zero prior evidence — black background, tiny stars, silence, then the
 * Moon, then the name, then the philosophy, only then the real screen.
 * No new copy: the sentence is the same one UniverseIntro already shows
 * every subsequent empty-conversation visit — this is just its first,
 * more deliberate telling.
 */
export function CinematicOpen({ onComplete }: { onComplete: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.2, ease: EASE_CALM }}
      className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-[#070B18]"
    >
      <svg viewBox="0 0 1000 1000" className="absolute inset-0 h-full w-full">
        <g transform="translate(500,500)">
          {stars.map((s, i) => (
            <motion.circle
              key={i}
              cx={s.x}
              cy={s.y}
              r={s.r}
              fill="#8B87A6"
              initial={{ opacity: 0 }}
              animate={{ opacity: s.opacity }}
              transition={{ duration: 2, ease: EASE_CALM }}
            />
          ))}
          <motion.circle
            cx={0}
            cy={0}
            r={22}
            fill="#F2EDE0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.85 }}
            transition={{ duration: 1.4, ease: EASE_CALM, delay: 1.6 }}
          />
        </g>
      </svg>

      <div className="relative flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, ease: EASE_CALM, delay: 3 }}
        >
          <Logo size="lg" />
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: EASE_CALM, delay: 4.2 }}
          className="mt-6 max-w-sm font-serif text-base italic leading-relaxed text-[#9C978A]"
        >
          Every student begins with countless possibilities.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: EASE_CALM, delay: 5.2 }}
          className="mt-2 max-w-sm font-serif text-base italic leading-relaxed text-[#9C978A]"
        >
          Aureon doesn't choose your future. It gradually understands it.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: EASE_CALM, delay: 6.2 }}
          onAnimationComplete={() => setTimeout(onComplete, 1400)}
          className="mt-4 max-w-sm text-sm font-medium leading-relaxed text-[#F2EDE0]"
        >
          Let's discover yours.
        </motion.p>
      </div>
    </motion.div>
  );
}
