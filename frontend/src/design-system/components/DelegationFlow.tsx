import { Field } from "./Field";
import type { Delegation } from "../../shared/api/types";

function displayName(agentName: string): string {
  return `${agentName.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())} Agent`;
}

/**
 * Aureon's universal delegation visualization — makes specialist
 * collaboration observable instead of invisible. One entry per real
 * delegation the mission actually recorded (Mission.delegations on the
 * backend); nothing here is inferred or guessed. Reused unmodified by
 * every mission-backed feature. A hairline-divided field, not a stack of
 * boxes — each entry is a beat in the same sequence, not an island.
 */
export function DelegationFlow({ delegations }: { delegations: Delegation[] }) {
  if (delegations.length === 0) return null;

  return (
    <Field divided>
      {delegations.map((d, i) => {
        const from = displayName(d.from_agent);
        const to = displayName(d.to_agent);
        return (
          <div key={i} className="py-4 first:pt-0 last:pb-0">
            <p className="text-sm text-ink">
              <span className="font-medium">{from}</span> delegated {d.capability} to{" "}
              <span className="font-medium">{to}</span>
            </p>
            <p className="mt-1 text-xs text-ink-muted">{d.reason}</p>
            <div className="mt-3 space-y-1 font-mono text-[0.68rem] tracking-wide text-ink-faint">
              <p>{to} working…</p>
              <p>{to.replace(" Agent", "")} findings received</p>
              <p>{from} reasoning resumed</p>
            </div>
          </div>
        );
      })}
    </Field>
  );
}
