import type { TraitSignal } from "../../../shared/api/types";

/**
 * Shared between CurrentUnderstandingPanel (Identity Discovery observatory)
 * and UniverseSummaryCard (Your Universe workspace tabs) — one canonical
 * mapping from the backend's 10 real trait names (domain/models/career_dna.py
 * TRAIT_NAMES) to a short human phrase, and one real threshold for what
 * counts as "strong" evidence. Nothing generated, nothing invented.
 */
export const STRONG_TRAIT_THRESHOLD = 0.4;

export const TRAIT_PHRASES: Record<string, string> = {
  curiosity: "Curious explorer",
  creativity: "Creative builder",
  analytical_thinking: "Analytical thinker",
  leadership: "Natural leader",
  communication: "Thoughtful communicator",
  learning_style: "Hands-on learner",
  motivation: "Purpose-driven achiever",
  values: "Principled thinker",
  work_preferences: "Focused collaborator",
  decision_style: "Deliberate decision-maker",
};

export function deriveTraitObservations(
  careerDna: Record<string, TraitSignal>,
  max = 4,
): string[] {
  return Object.entries(careerDna)
    .filter(([name, signal]) => (signal.score ?? 0) >= STRONG_TRAIT_THRESHOLD && TRAIT_PHRASES[name])
    .sort(([, a], [, b]) => (b.score ?? 0) - (a.score ?? 0))
    .slice(0, max)
    .map(([name]) => TRAIT_PHRASES[name]);
}
