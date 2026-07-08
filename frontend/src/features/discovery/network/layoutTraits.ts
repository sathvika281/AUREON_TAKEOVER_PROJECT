import type { TraitSignal } from "../../../shared/api/types";

/**
 * Canonical trait order, mirroring the backend's fixed vocabulary
 * (backend/src/aureon/domain/models/career_dna.py TRAIT_NAMES). A trait's
 * angle is derived from its position in this fixed list — not from the
 * count of currently-visible traits — so a given trait always claims the
 * same "place" in the graph regardless of which others exist yet. Only
 * traits actually present in career_dna are rendered; there are no empty
 * placeholder slots for traits with zero evidence.
 */
export const TRAIT_ORDER = [
  "curiosity",
  "creativity",
  "analytical_thinking",
  "leadership",
  "communication",
  "learning_style",
  "motivation",
  "values",
  "work_preferences",
  "decision_style",
] as const;

const MIN_RADIUS = 72;
const MAX_RADIUS = 208;
const MIN_SIZE = 34;
const MAX_SIZE = 64;
const MIN_OPACITY = 0.35;
const MAX_OPACITY = 1;

/** Qualitative traits (no numeric score, summary-only) still deserve a
 * visible-but-distant presence rather than vanishing entirely. */
const BASELINE_SCORE = 0.12;

export interface TraitNodeLayout {
  name: string;
  label: string;
  score: number | null;
  summary: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
}

function effectiveScore(score: number | null): number {
  const s = score ?? BASELINE_SCORE;
  return Math.max(0, Math.min(1, s));
}

export function traitLabel(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Pure function: current Career DNA -> node positions/sizes. Kept free of
 * rendering so the score -> geometry mapping is unit-testable on its own.
 */
export function layoutTraits(traits: Record<string, TraitSignal>): TraitNodeLayout[] {
  return Object.entries(traits).map(([name, signal]) => {
    const canonicalIndex = TRAIT_ORDER.indexOf(name as (typeof TRAIT_ORDER)[number]);
    const slot = canonicalIndex >= 0 ? canonicalIndex : TRAIT_ORDER.length;
    const angle = (slot / TRAIT_ORDER.length) * Math.PI * 2 - Math.PI / 2;

    const s = effectiveScore(signal.score);
    const radius = MAX_RADIUS - s * (MAX_RADIUS - MIN_RADIUS);

    return {
      name,
      label: traitLabel(name),
      score: signal.score,
      summary: signal.summary,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      size: MIN_SIZE + s * (MAX_SIZE - MIN_SIZE),
      opacity: MIN_OPACITY + s * (MAX_OPACITY - MIN_OPACITY),
    };
  });
}
