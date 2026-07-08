import type { CareerHypothesis, TraitSignal } from "../../../shared/api/types";
import { traitLabel } from "../network/layoutTraits";

/**
 * Honest three-tier derivation of "why are we doing this today" — no
 * fabricated dual-hypothesis dilemma text, since the API doesn't hand us
 * that framing. Deliberately simpler prose than a polished illustrative
 * example would suggest.
 */
export function deriveTodaysFocus(
  hypotheses: CareerHypothesis[],
  careerDna: Record<string, TraitSignal>,
): string {
  const topHypothesis = [...hypotheses].sort((a, b) => b.confidence - a.confidence)[0];
  if (topHypothesis && topHypothesis.missing_evidence.length > 0) {
    return `We're trying to understand more about your ${topHypothesis.missing_evidence[0]} before treating "${topHypothesis.career_name}" as more than a guess.`;
  }

  const traitNames = Object.keys(careerDna).map(traitLabel);
  if (traitNames.length > 0) {
    return `We're still mapping out what draws you in — ${traitNames.join(", ")}.`;
  }

  return "We're just getting started — every conversation, reflection, and small experiment adds a piece of the picture.";
}
