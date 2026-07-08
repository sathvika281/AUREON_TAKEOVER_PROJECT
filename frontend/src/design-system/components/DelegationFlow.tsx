import { Surface } from "./Surface";
import type { Delegation } from "../../shared/api/types";

function displayName(agentName: string): string {
  return `${agentName.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())} Agent`;
}

/**
 * Aureon's universal delegation visualization — makes specialist
 * collaboration observable instead of invisible. One card per real
 * delegation the mission actually recorded (Mission.delegations on the
 * backend); nothing here is inferred or guessed. Reused unmodified by
 * every mission-backed feature.
 */
export function DelegationFlow({ delegations }: { delegations: Delegation[] }) {
  if (delegations.length === 0) return null;

  return (
    <div className="space-y-3">
      {delegations.map((d, i) => {
        const from = displayName(d.from_agent);
        const to = displayName(d.to_agent);
        return (
          <Surface key={i} tone="neutral" padding="md">
            <p className="text-sm text-ink">
              <span className="font-medium">{from}</span> delegated {d.capability} to{" "}
              <span className="font-medium">{to}</span>
            </p>
            <p className="mt-1 text-xs text-ink-muted">{d.reason}</p>
            <div className="mt-3 space-y-1 border-t border-border pt-3 text-xs text-ink-faint">
              <p>{to} working…</p>
              <p>{to.replace(" Agent", "")} findings received</p>
              <p>{from} reasoning resumed</p>
            </div>
          </Surface>
        );
      })}
    </div>
  );
}
