import { humanizeMilestone } from "./milestoneCopy";
import { relativeTime } from "../notebook/relativeTime";
import type { NotebookEntry } from "../../../shared/api/types";

/**
 * The mockup reference's aesthetic (a thin mono status strip, a pulsing
 * "live" dot), none of its fabricated numbers. Every value here is real:
 * the actual understanding_stage, the actual notebook entry count, the
 * actual timestamp of the most recent real entry. If there's nothing
 * real to show for a field, that field doesn't render — never a
 * placeholder dash standing in for data that doesn't exist yet.
 */
export function LiveStatusBar({
  understandingStage,
  notebookEntries,
}: {
  understandingStage: string;
  notebookEntries: NotebookEntry[];
}) {
  const { friendly, technical } = humanizeMilestone(understandingStage);
  const latest = [...notebookEntries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];

  return (
    <div className="pointer-events-none flex flex-wrap items-center gap-x-6 gap-y-1 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-[#8C877A]">
      <span>
        {friendly} <span className="text-[#6E6A5E]">({technical})</span>
      </span>
      <span>
        NOTEBOOK_ENTRIES <span className="text-[#F2EDE0]">{notebookEntries.length}</span>
      </span>
      {latest && (
        <span>
          LAST_UPDATE <span className="text-[#F2EDE0]">{relativeTime(new Date(latest.created_at).getTime())}</span>
        </span>
      )}
      <span className="ml-auto flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#F2EDE0]" />
        LIVE
      </span>
    </div>
  );
}
