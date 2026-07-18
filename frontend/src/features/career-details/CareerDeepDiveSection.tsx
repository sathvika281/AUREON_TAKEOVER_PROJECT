import { Surface } from "../../design-system/components/Surface";
import { Badge } from "../../design-system/components/Badge";

/**
 * Explore Polish Batch — "what does a real day/week actually look
 * like," distinct from the higher-level `RealitySection` narrative.
 */
export function CareerDeepDiveSection({
  dayInTheLife,
  weeklyRoutine,
  dailyTools,
  careerProgression,
}: {
  dayInTheLife: string;
  weeklyRoutine: string;
  dailyTools: string[];
  careerProgression: string[];
}) {
  if (!dayInTheLife && !weeklyRoutine && dailyTools.length === 0 && careerProgression.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      {dayInTheLife && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">A day in this career</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{dayInTheLife}</p>
        </div>
      )}
      {weeklyRoutine && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">A week in this career</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{weeklyRoutine}</p>
        </div>
      )}
      {dailyTools.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Everyday tools</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {dailyTools.map((tool) => (
              <Badge key={tool}>{tool}</Badge>
            ))}
          </div>
        </div>
      )}
      {careerProgression.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Career progression</p>
          <div className="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">
            {careerProgression.map((step, i) => (
              <span key={step} className="flex items-center gap-1.5">
                <span>{step}</span>
                {i < careerProgression.length - 1 && <span className="text-ink-faint">→</span>}
              </span>
            ))}
          </div>
        </div>
      )}
    </Surface>
  );
}
