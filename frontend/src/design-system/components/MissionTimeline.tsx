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
    <div className="space-y-4 border-l border-border pl-5">
      {stages.map((stage, i) => (
        <div key={i} className="relative">
          <span className="absolute -left-[23px] top-1.5 h-1.5 w-1.5 rounded-full border border-accent-soft bg-accent-soft" />
          <p className="font-mono text-[0.62rem] tracking-[0.14em] text-ink-faint">
            {String(i + 1).padStart(2, "0")}
          </p>
          <p className="mt-0.5 text-sm text-ink">{stage}</p>
        </div>
      ))}
    </div>
  );
}
