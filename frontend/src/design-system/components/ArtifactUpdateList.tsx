/**
 * Aureon's universal artifact-update view — renders only what the
 * backend's own route/specialist decided changed (each response's
 * `artifacts_updated` list). This component never infers or guesses what
 * was updated; that decision stays owned by the specialist, matching the
 * V4–V6 capability-ownership discipline.
 */
export function ArtifactUpdateList({ artifacts }: { artifacts: string[] }) {
  if (artifacts.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {artifacts.map((artifact) => (
        <span
          key={artifact}
          className="rounded-full border border-accent/30 bg-accent/10 px-3 py-1.5 text-xs text-accent-soft"
        >
          {artifact}
        </span>
      ))}
    </div>
  );
}
