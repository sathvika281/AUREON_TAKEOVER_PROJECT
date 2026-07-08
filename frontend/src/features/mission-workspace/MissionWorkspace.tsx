import type { ReactNode } from "react";

import { AgentPanel } from "../../design-system/components/AgentPanel";
import { ArtifactUpdateList } from "../../design-system/components/ArtifactUpdateList";
import { DelegationFlow } from "../../design-system/components/DelegationFlow";
import { EvidenceCard } from "../../design-system/components/EvidenceCard";
import { MissionTimeline } from "../../design-system/components/MissionTimeline";
import { Surface } from "../../design-system/components/Surface";
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
    <div className="space-y-8">
      <Surface tone="raised" padding="lg">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Mission</p>
        <h2 className="mt-1.5 text-lg font-medium text-ink">Investigation Timeline</h2>
        <div className="mt-4">
          <MissionTimeline stages={snapshot.stages} />
        </div>
      </Surface>

      <div>
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Agents</p>
        <AgentPanel agents={snapshot.agents} />
      </div>

      {snapshot.delegations.length > 0 && (
        <div>
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Delegation</p>
          <DelegationFlow delegations={snapshot.delegations} />
        </div>
      )}

      {snapshot.tools.length > 0 && (
        <div>
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Tool Execution</p>
          <ToolExecutionList tools={snapshot.tools} />
        </div>
      )}

      {snapshot.evidence.length > 0 && (
        <div>
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Evidence</p>
          <div className="space-y-3">
            {snapshot.evidence.map((e, i) => (
              <EvidenceCard key={i} evidence={e} />
            ))}
          </div>
        </div>
      )}

      {artifactsUpdated.length > 0 && (
        <div>
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Artifacts Updated</p>
          <ArtifactUpdateList artifacts={artifactsUpdated} />
        </div>
      )}

      <div className="border-t border-border pt-8">
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Final Report</p>
        {finalReport}
      </div>
    </div>
  );
}
