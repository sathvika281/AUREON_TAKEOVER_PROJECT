import { useReducedMotion as useFramerReducedMotion } from "framer-motion";

/** Single source of truth for "should heavy motion be dampened." */
export const useReducedMotion = useFramerReducedMotion;

/**
 * Calm, deliberate easing — no springy/bouncy game-feel anywhere in the
 * product. Framer Motion cubic-bezier tuples. Nothing here ever bounces,
 * overshoots, or spins — everything arrives, settles, breathes.
 */
export const EASE_CALM = [0.16, 1, 0.3, 1] as const;

/** A sharper expo-out, reserved for something settling into place — an
 * instrument reading resolving, a location being arrived at. Layered on
 * top of EASE_CALM's default for the Instrument Panel's 20% precision
 * note; it never replaces EASE_CALM for ordinary fades. */
export const EASE_ARRIVE = [0.22, 1, 0.36, 1] as const;

export const DURATION = {
  quick: 0.3,
  settle: 0.6,
  drift: 0.9,
  reveal: 1.6,
  // An instrument-panel snap — a readout resolving, not a page fading in.
  arrive: 0.45,
  // The cinematic/silence register — the longest, most deliberate beat.
  breathe: 2.2,
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
