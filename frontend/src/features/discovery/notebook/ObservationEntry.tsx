import { motion } from "framer-motion";
import { PenLine } from "lucide-react";

import { Badge } from "../../../design-system/components/Badge";
import type { NotebookEntry } from "../../../shared/api/types";
import { relativeTime } from "./relativeTime";

const toneForLabel: Record<string, "warm" | "cool" | "neutral"> = {
  High: "warm",
  Medium: "cool",
  Emerging: "neutral",
};

/**
 * A brief "Aureon is writing" moment precedes the observation settling
 * in — the notebook should read as something being composed, not a log
 * rendering instantly. Renders a server-persisted `NotebookEntry` of
 * kind "observation".
 */
export function ObservationEntry({ entry }: { entry: NotebookEntry }) {
  const label = entry.confidence_label ?? "Emerging";

  return (
    <div className="border-l border-border py-2.5 pl-4">
      <div className="relative">
        <motion.span
          initial={{ opacity: 1 }}
          animate={{ opacity: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
          className="absolute left-0 top-0.5 text-accent-soft"
        >
          <PenLine size={13} />
        </motion.span>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="pl-5 text-sm leading-relaxed text-ink-muted"
        >
          {entry.text}
        </motion.p>
      </div>
      <div className="mt-1.5 flex items-center gap-2 pl-5 text-[0.68rem] text-ink-faint">
        <span>{entry.source}</span>
        <span>·</span>
        <span>{relativeTime(new Date(entry.created_at).getTime())}</span>
        <Badge tone={toneForLabel[label] ?? "neutral"} className="ml-auto">
          {label}
        </Badge>
      </div>
    </div>
  );
}
