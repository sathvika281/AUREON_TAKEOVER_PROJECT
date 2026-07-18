/**
 * Presentation-only mapping over the backend's real 6-value
 * understanding_stage literal (same source milestoneCopy.ts reads) — the
 * Moon's phase is never derived from a frontend-invented confidence
 * cutoff, only from this real, discrete, backend-computed stage. Exactly
 * one preset per real stage, so the mapping is trivially exhaustive and
 * testable, matching the discipline milestoneCopy.ts already established.
 */
export interface MoonPhase {
  name: string;
  /** 0 = New Moon (unlit), 1 = Full Moon (fully lit). */
  litFraction: number;
}

const MOON_PHASES: Record<string, MoonPhase> = {
  Seed: { name: "New Moon", litFraction: 0.06 },
  Explorer: { name: "Waxing Crescent", litFraction: 0.22 },
  "Patterns Emerging": { name: "First Quarter", litFraction: 0.5 },
  "Identity Taking Shape": { name: "Waxing Gibbous", litFraction: 0.72 },
  "Career DNA Forming": { name: "Waxing Gibbous", litFraction: 0.88 },
  "Decision Ready": { name: "Full Moon", litFraction: 1 },
};

const DEFAULT_PHASE: MoonPhase = MOON_PHASES.Seed;

export function moonPhaseFor(understandingStage: string): MoonPhase {
  return MOON_PHASES[understandingStage] ?? DEFAULT_PHASE;
}

/**
 * The classic two-arc lunar-phase SVG path: an outer arc along the fixed
 * lit-side (right) hemisphere, an inner arc along a terminator ellipse
 * whose horizontal radius encodes litFraction. At litFraction=0 the
 * inner arc traces the *same* side as the outer arc (cancelling to zero
 * area — invisible); at 0.5 it degenerates to the vertical diameter (a
 * true half-moon); at 1 it traces the *opposite* side, completing a full
 * circle. Pure geometry, zero randomness.
 */
export function moonLitPath(radius: number, litFraction: number): string {
  const clamped = Math.max(0, Math.min(1, litFraction));
  const rx = radius * Math.abs(1 - 2 * clamped);
  const innerSweep = clamped < 0.5 ? 0 : 1;
  return `M 0,${-radius} A ${radius},${radius} 0 0,1 0,${radius} A ${rx},${radius} 0 0,${innerSweep} 0,${-radius} Z`;
}
