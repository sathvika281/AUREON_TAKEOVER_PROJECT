/**
 * Aureon's universal mission timeline — the backbone of the Mission
 * Workspace. Renders exactly the stages a mission actually recorded
 * (Mission.stage_log on the backend); never a fabricated step. Reused
 * unmodified by every mission-backed feature — it only ever receives a
 * plain list of real stage strings, never anything feature-specific.
 */
export function MissionTimeline({ stages }: { stages: string[] }) {
  if (stages.length === 0) return null;

  return (
    <div className="space-y-3">
      {stages.map((stage, i) => (
        <div key={i} className="flex gap-3 border-l-2 border-border pl-3">
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Step {i + 1}</p>
            <p className="mt-0.5 text-sm text-ink">{stage}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
