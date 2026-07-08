import { Surface } from "../../design-system/components/Surface";
import type { FutureLens } from "../../shared/api/types";

const STAGES: { key: keyof FutureLens; label: string }[] = [
  { key: "demand_2030", label: "2030" },
  { key: "demand_2035", label: "2035" },
  { key: "demand_2040", label: "2040" },
];

/**
 * Today -> 2030 -> 2035 -> 2040, per career. Deliberately calm framing —
 * no fear-based "AI will replace this" language anywhere in the data or
 * the layout.
 */
export function TimelineComparison({
  careerName,
  futureLens,
}: {
  careerName: string;
  futureLens: FutureLens;
}) {
  return (
    <Surface tone="raised" padding="md">
      <p className="text-sm font-medium text-ink">{careerName}</p>
      <p className="mt-2 text-xs leading-relaxed text-ink-muted">{futureLens.timeline_narrative}</p>

      <div className="mt-4 grid grid-cols-4 gap-2 border-t border-border pt-4">
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Today</p>
          <p className="mt-1 text-xs leading-relaxed text-ink-muted">{futureLens.ai_impact}</p>
        </div>
        {STAGES.map(({ key, label }) => (
          <div key={key}>
            <p className="text-[0.65rem] uppercase tracking-widest text-accent/80">{label}</p>
            <p className="mt-1 text-xs leading-relaxed text-ink-muted">{futureLens[key] as string}</p>
          </div>
        ))}
      </div>

      {futureLens.skills_becoming_valuable.length > 0 && (
        <div className="mt-4 border-t border-border pt-3">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
            Skills becoming more valuable
          </p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {futureLens.skills_becoming_valuable.map((skill) => (
              <span key={skill} className="rounded-full bg-white/5 px-2.5 py-1 text-xs text-ink-muted">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </Surface>
  );
}
