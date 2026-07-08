import { Badge } from "./Badge";
import type { ToolExecution } from "../../shared/api/types";

const STATUS_LABEL: Record<ToolExecution["status"], string> = {
  completed: "Completed",
  failed: "Failed",
  not_connected: "Not Connected",
};

const STATUS_TONE: Record<ToolExecution["status"], "warm" | "cool" | "neutral"> = {
  completed: "warm",
  failed: "cool",
  not_connected: "neutral",
};

function toolLabel(toolName: string): string {
  return toolName.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Aureon's universal tool-execution view — sourced directly from
 * ToolResult.status on the backend, never fabricated. Reused unmodified
 * by every specialist's toolset (URL Reader, Document Reader, Curriculum
 * Reader, Publication Reader, Opportunity Search, ...).
 */
export function ToolExecutionList({ tools }: { tools: ToolExecution[] }) {
  if (tools.length === 0) return null;

  return (
    <div className="space-y-2">
      {tools.map((tool, i) => (
        <div key={i} className="rounded-xl border border-border bg-surface px-3 py-2.5">
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm text-ink">{toolLabel(tool.tool_name)}</span>
            <Badge tone={STATUS_TONE[tool.status]}>{STATUS_LABEL[tool.status]}</Badge>
          </div>
          {tool.explanation && <p className="mt-1 text-xs text-ink-faint">{tool.explanation}</p>}
        </div>
      ))}
    </div>
  );
}
