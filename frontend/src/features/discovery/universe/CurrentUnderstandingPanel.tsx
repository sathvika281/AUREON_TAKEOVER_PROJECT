import type { TraitSignal } from "../../../shared/api/types";
import { deriveTraitObservations } from "./traitObservations";

/**
 * Identity Discovery does not recommend careers — it explains what
 * Aureon is noticing about the student. This is the one place that
 * distinction has to be visible in plain language: recurring, evidenced
 * trait patterns, never a career suggestion. Nothing generated, nothing
 * invented — see traitObservations.ts for the shared real-data mapping.
 * Styled as Aureon's own field notes — no border, no card, just text
 * living in the scene's negative space.
 */
export function CurrentUnderstandingPanel({
  careerDna,
  className = "",
}: {
  careerDna: Record<string, TraitSignal>;
  className?: string;
}) {
  const observations = deriveTraitObservations(careerDna);

  return (
    <div className={`max-w-xs ${className}`}>
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#D9B87A]">
        Current Understanding
      </p>

      {observations.length === 0 ? (
        <p className="mt-2 font-serif text-base italic leading-relaxed text-[#9C978A]">
          Just beginning to reveal itself — nothing has been evidenced yet.
        </p>
      ) : (
        <>
          <p className="mt-2 text-sm leading-relaxed text-[#9C978A]">
            Across our conversations, Aureon is noticing recurring patterns.
          </p>
          <ul className="mt-3 space-y-1.5">
            {observations.map((phrase) => (
              <li key={phrase} className="font-serif text-lg leading-snug text-[#F2EDE0]">
                {phrase}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs leading-relaxed text-[#6E6A5E]">
            More conversations will strengthen or reshape these observations.
          </p>
        </>
      )}
    </div>
  );
}
