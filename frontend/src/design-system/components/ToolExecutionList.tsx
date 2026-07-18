import { Badge } from "./Badge";
import { Field } from "./Field";
import type { ToolExecution } from "../../shared/api/types";

const STATUS_LABEL: Record<ToolExecution["status"], string> = {
  completed: "Completed",
  failed: "Failed",
  not_connected: "Not Connected",
};

const STATUS_TONE: Record<ToolExecution["status"], "success" | "cool" | "neutral"> = {
  completed: "success",
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
 * Reader, Publication Reader, Opportunity Search, ...). A hairline-divided
 * readout instead of a stack of bordered boxes.
 */
export function ToolExecutionList({ tools }: { tools: ToolExecution[] }) {
  if (tools.length === 0) return null;

  return (
    <Field divided>
      {tools.map((tool, i) => (
        <div key={i} className="flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0">
          <div>
            <span className="text-sm text-ink">{toolLabel(tool.tool_name)}</span>
            {tool.explanation && <p className="mt-1 text-xs text-ink-faint">{tool.explanation}</p>}
          </div>
          <Badge tone={STATUS_TONE[tool.status]}>{STATUS_LABEL[tool.status]}</Badge>
        </div>
      ))}
    </Field>
  );
}
