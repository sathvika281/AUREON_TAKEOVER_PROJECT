import { Check, Compass, Eye, Handshake, Target } from "lucide-react";

import { cn } from "../../design-system/cn";
import { Surface } from "../../design-system/components/Surface";
import type { StageProgress } from "../../shared/api/types";

const STAGES: { key: keyof StageProgress; label: string; icon: typeof Eye }[] = [
  { key: "discover", label: "Discover", icon: Eye },
  { key: "explore", label: "Explore", icon: Compass },
  { key: "connect", label: "Connect", icon: Handshake },
];

/**
 * Orients the student in the same 4-stage journey the rest of Aureon
 * already uses (see `journeyConfig.ts`'s `StageId`). Discover/Explore/
 * Connect are real engagement checks (`stageProgress`, computed from
 * already-persisted profile data); Decide is always shown as the
 * current stage — this screen. `overallReadinessPercent` is the mean
 * of every card's own Decision Progress, not a new number.
 */
export function DecisionJourneyHeader({
  stageProgress,
  overallReadinessPercent,
}: {
  stageProgress: StageProgress;
  overallReadinessPercent: number;
}) {
  return (
    <Surface tone="neutral" padding="md" className="mb-6">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Decision Journey</p>
      <div className="mt-3 flex flex-wrap items-center gap-4">
        {STAGES.map(({ key, label, icon: Icon }) => {
          const done = stageProgress[key];
          return (
            <div key={key} className="flex items-center gap-1.5">
              <span
                className={cn(
                  "flex h-6 w-6 items-center justify-center rounded-full border",
                  done ? "border-accent-soft/40 bg-accent/10 text-accent-soft" : "border-border text-ink-faint",
                )}
              >
                {done ? <Check size={13} /> : <Icon size={13} />}
              </span>
              <span className={cn("text-xs", done ? "text-ink" : "text-ink-faint")}>{label}</span>
            </div>
          );
        })}
        <div className="flex items-center gap-1.5">
          <span className="flex h-6 w-6 items-center justify-center rounded-full border border-accent-soft/40 bg-accent/10 text-accent-soft">
            <Target size={13} />
          </span>
          <span className="text-xs text-ink">Decide</span>
        </div>
      </div>
      <p className="mt-3 text-xs leading-relaxed text-ink-muted">
        You've covered <span className="text-accent-soft">{overallReadinessPercent}%</span> of what's useful to
        know before making a confident decision.
      </p>
    </Surface>
  );
}
