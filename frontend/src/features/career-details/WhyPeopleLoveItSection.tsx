import { Surface } from "../../design-system/components/Surface";
import type { CareerBranch } from "../../shared/api/types";

/**
 * "What this career actually is" + "why people love it" + real
 * specialization branches — Explore Batch 1's answer to "what does this
 * world actually feel like," not "what salary does it pay."
 */
export function WhyPeopleLoveItSection({
  description,
  whyPeopleLoveIt,
  branches,
}: {
  description: string;
  whyPeopleLoveIt: string;
  branches: CareerBranch[];
}) {
  if (!description && !whyPeopleLoveIt && branches.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      {description && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">What this career actually is</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{description}</p>
        </div>
      )}
      {whyPeopleLoveIt && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Why people love it</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{whyPeopleLoveIt}</p>
        </div>
      )}
      {branches.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Specialization paths</p>
          <div className="mt-2 space-y-2">
            {branches.map((branch) => (
              <div key={branch.name}>
                <p className="text-sm text-ink">{branch.name}</p>
                <p className="text-xs text-ink-faint">{branch.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </Surface>
  );
}
