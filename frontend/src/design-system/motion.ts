import { useReducedMotion as useFramerReducedMotion } from "framer-motion";

/** Single source of truth for "should heavy motion be dampened." */
export const useReducedMotion = useFramerReducedMotion;

/**
 * Calm, deliberate easing — no springy/bouncy game-feel anywhere in the
 * product. Framer Motion cubic-bezier tuples.
 */
export const EASE_CALM = [0.16, 1, 0.3, 1] as const;

export const DURATION = {
  quick: 0.3,
  settle: 0.6,
} as const;

export const fadeInUp = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: { duration: DURATION.settle, ease: EASE_CALM },
};

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: DURATION.settle, ease: EASE_CALM },
};
