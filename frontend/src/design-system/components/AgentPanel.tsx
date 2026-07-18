import { cn } from "../cn";
import type { AgentStatus } from "../../shared/api/types";

/**
 * Aureon's universal specialist roster — which agents participated in a
 * mission and which didn't. Only two real states are ever shown:
 * Completed and Not Required. There is no in-flight "Waiting" state to
 * observe in a synchronous request/response cycle, so this never
 * fabricates one. Reused unmodified by every mission-backed feature. A
 * signal dot carries the state, not a filled badge pill.
 */
export function AgentPanel({ agents }: { agents: AgentStatus[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {agents.map((agent) => (
        <div
          key={agent.name}
          className="flex items-center gap-2.5 rounded-lg border border-border px-3 py-2"
        >
          <span
            className={cn(
              "h-1.5 w-1.5 shrink-0 rounded-full",
              agent.status === "completed" ? "bg-accent-soft" : "bg-ink-faint/40",
            )}
          />
          <span className="text-sm text-ink">{agent.display_name}</span>
          <span className="font-mono text-[0.6rem] uppercase tracking-wide text-ink-faint">
            {agent.status === "completed" ? "Completed" : "Not required"}
          </span>
        </div>
      ))}
    </div>
  );
}
