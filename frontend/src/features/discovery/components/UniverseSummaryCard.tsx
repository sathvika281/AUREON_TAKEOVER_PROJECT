import { Badge } from "../../../design-system/components/Badge";
import { Surface } from "../../../design-system/components/Surface";
import type { CareerHypothesis, TraitSignal } from "../../../shared/api/types";
import { humanizeMilestone } from "../universe/milestoneCopy";
import { deriveTraitObservations } from "../universe/traitObservations";

function deriveNorthStar(hypotheses: CareerHypothesis[]): CareerHypothesis | null {
  const live = hypotheses.filter((h) => h.status !== "discarded");
  if (live.length === 0) return null;
  return [...live].sort((a, b) => b.confidence - a.confidence)[0];
}

/**
 * The first thing seen on any Your Universe tab — "where do I currently
 * stand," not a row of tab labels. Built entirely from data
 * DiscoveryContext already exposes; nothing computed here is new. Honest
 * empty states throughout when there isn't yet a real North Star or
 * strong trait.
 */
export function UniverseSummaryCard({
  hypotheses,
  careerDna,
  confidenceScore,
  understandingStage,
}: {
  hypotheses: CareerHypothesis[];
  careerDna: Record<string, TraitSignal>;
  confidenceScore: number;
  understandingStage: string;
}) {
  const northStar = deriveNorthStar(hypotheses);
  const traits = deriveTraitObservations(careerDna, 2);
  const { friendly } = humanizeMilestone(understandingStage);

  return (
    <Surface tone="neutral" padding="md">
      <div className="grid gap-6 sm:grid-cols-4">
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">North Star</p>
          <p className="mt-1.5 text-sm font-medium text-ink">
            {northStar ? northStar.career_name : "Not yet visible"}
          </p>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Confidence</p>
          <p className="mt-1.5 text-sm font-medium text-ink">{Math.round(confidenceScore * 100)}%</p>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Strongest Traits</p>
          <p className="mt-1.5 text-sm font-medium text-ink">
            {traits.length > 0 ? traits.join(", ") : "Just beginning to reveal itself"}
          </p>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Universe Status</p>
          <div className="mt-1.5">
            <Badge tone="warm">{friendly}</Badge>
          </div>
        </div>
      </div>
    </Surface>
  );
}
