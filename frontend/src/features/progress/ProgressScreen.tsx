import { GitCompare, Lightbulb, ListChecks, ScanSearch, Sprout } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import type { ProgressDirection, ProgressReport } from "../../shared/api/types";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useProgressContext } from "./ProgressContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: ScanSearch,
    title: "Reads your existing evidence trail",
    description: "Career DNA, the Discovery Notebook, Reflection Journal, Career Exploration History, Decision Lab activity — nothing new to fill in, nothing invented.",
  },
  {
    icon: GitCompare,
    title: "Compares recent activity to what came before",
    description: "Every dimension's direction (improving, steady, slowing) is a real comparison between this week and the weeks before it — never a guess.",
  },
  {
    icon: Lightbulb,
    title: "Explains why, grounded in that evidence",
    description: "The narrative only ever describes what the real numbers already show — it never asserts a direction on its own.",
  },
  {
    icon: ListChecks,
    title: "Ranks what to focus on next",
    description: "Every priority names the specific evidence behind it — never a generic tip with nothing backing it.",
  },
];

const DIRECTION_LABEL: Record<ProgressDirection, string> = {
  improving: "Improving",
  steady: "Steady",
  slowing: "Slowing",
  not_enough_evidence: "Not Enough Evidence",
};

const DIRECTION_TONE: Record<ProgressDirection, "warm" | "cool" | "neutral"> = {
  improving: "warm",
  steady: "cool",
  slowing: "neutral",
  not_enough_evidence: "neutral",
};

function progressReportBody(report: ProgressReport) {
  return (
    <>
      <Surface tone="raised" padding="md">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Overall Progress</p>
        <p className="mt-2 text-sm leading-relaxed text-ink">{report.overall_narrative}</p>
      </Surface>

      <div className="mt-8 space-y-4">
        <p className="px-1 text-xs uppercase tracking-widest text-ink-faint">Dimensions</p>
        {report.dimensions.map((dim) => (
          <Surface key={dim.key} tone="neutral" padding="md">
            <div className="flex items-baseline justify-between">
              <h3 className="text-sm font-medium text-ink">{dim.label}</h3>
              <Badge tone={DIRECTION_TONE[dim.direction]}>{DIRECTION_LABEL[dim.direction]}</Badge>
            </div>
            {dim.reasoning && (
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{dim.reasoning}</p>
            )}
            <ul className="mt-2 space-y-0.5">
              {dim.evidence_summary.map((fact, i) => (
                <li key={i} className="text-xs text-ink-faint">
                  <span className="text-accent-soft">＋</span> {fact}
                </li>
              ))}
            </ul>
          </Surface>
        ))}
      </div>

      {(report.growing_strengths.length > 0 || report.areas_slowing_down.length > 0) && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {report.growing_strengths.length > 0 && (
            <Surface tone="neutral" padding="md">
              <p className="text-[0.65rem] uppercase tracking-widest text-accent-soft">Growing Strengths</p>
              <ul className="mt-2 space-y-1">
                {report.growing_strengths.map((s, i) => (
                  <li key={i} className="text-sm text-ink-muted">{s}</li>
                ))}
              </ul>
            </Surface>
          )}
          {report.areas_slowing_down.length > 0 && (
            <Surface tone="neutral" padding="md">
              <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Areas Slowing Down</p>
              <ul className="mt-2 space-y-1">
                {report.areas_slowing_down.map((s, i) => (
                  <li key={i} className="text-sm text-ink-muted">{s}</li>
                ))}
              </ul>
            </Surface>
          )}
        </div>
      )}

      {report.recent_improvements.length > 0 && (
        <div className="mt-8">
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Recent Improvements</p>
          <Surface tone="neutral" padding="md">
            <ul className="space-y-1">
              {report.recent_improvements.map((s, i) => (
                <li key={i} className="text-sm text-ink-muted">{s}</li>
              ))}
            </ul>
          </Surface>
        </div>
      )}

      <div className="mt-8">
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Timeline</p>
        <div className="space-y-3">
          {report.timeline.map((window) => (
            <div key={window.label} className="flex gap-3 border-l-2 border-border pl-3">
              <div>
                <p className="text-[0.65rem] uppercase tracking-widest text-accent-soft">{window.label}</p>
                <p className="mt-1 text-sm text-ink-muted">{window.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {report.next_priorities.length > 0 && (
        <div className="mt-8">
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Next Priorities</p>
          <div className="space-y-3">
            {report.next_priorities.map((priority) => (
              <Surface key={priority.rank} tone="raised" padding="md">
                <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
                  Priority {priority.rank}
                </p>
                <p className="mt-1 text-sm font-medium text-ink">{priority.action}</p>
                <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                  <span className="text-ink-faint">Evidence: </span>
                  {priority.evidence}
                </p>
              </Surface>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

export function ProgressScreen() {
  const { report, isAnalyzing, error, analyzeProgress } = useProgressContext();

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Progress Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Not a checklist, not a streak counter — a continuous read on how your journey is
        actually evolving, reasoned from evidence Aureon already has about you.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How Progress Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6">
        <Button onClick={analyzeProgress} disabled={isAnalyzing}>
          {isAnalyzing ? "Analyzing…" : report ? "Re-analyze My Progress" : "Analyze My Progress"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {!report && !isAnalyzing && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={Sprout}
            title="No Analysis Run Yet"
            description="Analyze your progress above to see how your journey is evolving across exploration, career clarity, decision confidence, reflection, and skill development."
          />
        </div>
      )}

      {report && report.insufficient_evidence && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={Sprout}
            title="Not Enough Evidence Yet"
            description={
              report.insufficient_evidence_reason ??
              "Aureon needs a broader evidence trail before it can reason about your progress responsibly."
            }
          />
        </div>
      )}

      {report && !report.insufficient_evidence && (
        <div className="mt-8">
          {report.mission ? (
            <MissionWorkspace
              snapshot={report.mission}
              artifactsUpdated={report.artifacts_updated}
              finalReport={progressReportBody(report)}
            />
          ) : (
            progressReportBody(report)
          )}
        </div>
      )}
    </div>
  );
}
