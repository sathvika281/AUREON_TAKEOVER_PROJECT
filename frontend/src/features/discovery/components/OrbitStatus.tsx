import { OrbitMark } from "../../../design-system/components/Marks";
import { Surface } from "../../../design-system/components/Surface";
import type { OrbitStatus as OrbitStatusData } from "../../../shared/api/types";
import { humanizeMilestone } from "../universe/milestoneCopy";

/**
 * A permanent, quiet reassurance widget — "where am I, what should I
 * focus on, what should I ignore" — never a dashboard stat. Purely
 * presentational: every field is real backend-computed state from the
 * Orbit Service (Discover Batch 1 backend migration) — this component
 * no longer computes any of it locally.
 */
export function OrbitStatus({ status }: { status: OrbitStatusData }) {
  const { friendly } = humanizeMilestone(status.current_orbit);

  return (
    <Surface tone="neutral" padding="md">
      <p className="flex items-center gap-1.5 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
        <OrbitMark size={13} />
        Orbit Status
      </p>

      <div className="mt-3 grid gap-5 sm:grid-cols-3">
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Current Orbit</p>
          <p className="mt-1.5 text-sm font-medium text-ink">{status.current_orbit}</p>
          <p className="mt-0.5 text-xs text-ink-faint">{friendly}</p>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Current Focus</p>
          <ul className="mt-1.5 space-y-1 text-sm text-ink-muted">
            {status.focus.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Don't Worry About</p>
          <ul className="mt-1.5 space-y-1 text-sm text-ink-muted">
            {status.avoid.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
      </div>

      <p className="mt-4 text-xs leading-relaxed text-ink-faint">{status.explanation}</p>
      <p className="mt-2 font-serif text-sm italic text-ink-muted">{status.message}</p>
    </Surface>
  );
}
