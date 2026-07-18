import type { ReactNode } from "react";

import { AgentPanel } from "../../design-system/components/AgentPanel";
import { ArtifactUpdateList } from "../../design-system/components/ArtifactUpdateList";
import { DelegationFlow } from "../../design-system/components/DelegationFlow";
import { EvidenceCard } from "../../design-system/components/EvidenceCard";
import { MissionTimeline } from "../../design-system/components/MissionTimeline";
import { ToolExecutionList } from "../../design-system/components/ToolExecutionList";
import type { MissionSnapshot } from "../../shared/api/types";

/**
 * Aureon's universal execution interface — not built for URL
 * Investigation, Mentor Match, Institution Match, or Progress
 * Intelligence specifically. It accepts only generic mission data and
 * never branches on which feature produced it; adding a future
 * mission-backed capability means passing it the same three props, with
 * zero changes to this component.
 *
 * Composition order: Mission -> Timeline (the backbone) -> Agents ->
 * Delegation -> Evidence -> Artifacts -> the caller's own Final Report,
 * rendered last and completely untouched.
 */
export function MissionWorkspace({
  snapshot,
  artifactsUpdated,
  finalReport,
}: {
  snapshot: MissionSnapshot;
  artifactsUpdated: string[];
  finalReport: ReactNode;
}) {
  return (
    <div className="space-y-10">
      <div>
        <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-ink-faint">
          Mission Command
        </p>
        <h2 className="mt-2 font-serif text-2xl italic text-ink">Investigation Timeline</h2>
        <div className="mt-6">
          <MissionTimeline stages={snapshot.stages} />
        </div>
      </div>

      <div>
        <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">Agents</p>
        <AgentPanel agents={snapshot.agents} />
      </div>

      {snapshot.delegations.length > 0 && (
        <div>
          <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">
            Delegation
          </p>
          <DelegationFlow delegations={snapshot.delegations} />
        </div>
      )}

      {snapshot.tools.length > 0 && (
        <div>
          <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">
            Tool Execution
          </p>
          <ToolExecutionList tools={snapshot.tools} />
        </div>
      )}

      {snapshot.evidence.length > 0 && (
        <div>
          <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">
            Evidence
          </p>
          <div className="space-y-3">
            {snapshot.evidence.map((e, i) => (
              <EvidenceCard key={i} evidence={e} />
            ))}
          </div>
        </div>
      )}

      {artifactsUpdated.length > 0 && (
        <div>
          <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">
            Artifacts Updated
          </p>
          <ArtifactUpdateList artifacts={artifactsUpdated} />
        </div>
      )}

      <div className="border-t border-border pt-10">
        <p className="mb-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-ink-faint">
          Final Report
        </p>
        {finalReport}
      </div>
    </div>
  );
}
