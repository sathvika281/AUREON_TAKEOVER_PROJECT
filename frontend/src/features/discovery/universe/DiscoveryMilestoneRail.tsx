import { humanizeMilestone } from "./milestoneCopy";

/**
 * Re-skins the real understanding_stage + understanding_narrative the
 * backend already computes — no new state, no percentage bar. The
 * technical stage name always stays visible in parens next to the
 * friendlier phrase.
 */
export function DiscoveryMilestoneRail({
  understandingStage,
  understandingNarrative,
  className = "",
}: {
  understandingStage: string;
  understandingNarrative: string;
  className?: string;
}) {
  const { friendly } = humanizeMilestone(understandingStage);

  return (
    <div className={className}>
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.16em] text-[#D9B87A]">{friendly}</p>
      <p className="mt-1.5 max-w-sm font-serif italic leading-relaxed text-[#9C978A]">
        {understandingNarrative}
      </p>
    </div>
  );
}
