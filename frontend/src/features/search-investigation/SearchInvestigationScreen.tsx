import { useState } from "react";
import { CheckCircle2, AlertTriangle, Search, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import type { Finding, SearchInvestigationResult } from "../../shared/api/types";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useSearchInvestigationContext } from "./SearchInvestigationContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: Search,
    title: "Investigates, never just recalls",
    description: "Plans real search queries and reads real trusted sources — never answers from memory alone.",
  },
  {
    icon: CheckCircle2,
    title: "Cross-verifies every claim",
    description: "Classifies each finding as supported, contradicted, mixed, or insufficient evidence — never presents uncertainty as fact.",
  },
  {
    icon: Sparkles,
    title: "Shows its sources honestly",
    description: "Wikipedia, arXiv, and Semantic Scholar are each shown as reached or unavailable — this never changes the conclusions themselves.",
  },
  {
    icon: ShieldAlert,
    title: "Never fabricates a conclusion",
    description: "If real evidence can't answer the question, Aureon says so rather than guessing.",
  },
];

const STATUS_LABEL: Record<Finding["status"], string> = {
  supported: "Supported",
  contradicted: "Contradicted",
  mixed: "Mixed",
  insufficient_evidence: "Insufficient Evidence",
};

const STATUS_TONE: Record<Finding["status"], "warm" | "cool" | "neutral"> = {
  supported: "warm",
  contradicted: "cool",
  mixed: "cool",
  insufficient_evidence: "neutral",
};

function investigationReport(result: SearchInvestigationResult) {
  return (
    <div className="space-y-4">
      {result.source_availability && (
        <Surface tone="raised" padding="md">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
            Sources Investigated ({result.source_availability.sources_retrieved}/{result.source_availability.total_sources} retrieved)
          </p>
          <div className="mt-2 flex flex-wrap gap-3 text-sm">
            {result.source_availability.sources.map((s) => (
              <span key={s.name} className="flex items-center gap-1.5 text-ink-muted">
                {s.reached ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-accent-soft" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5 text-ink-faint" />
                )}
                {s.name}
                {s.note && <span className="text-ink-faint">({s.note})</span>}
              </span>
            ))}
          </div>
        </Surface>
      )}

      {result.overall_summary && (
        <Surface tone="neutral" padding="md">
          <p className="text-sm leading-relaxed text-ink">{result.overall_summary}</p>
        </Surface>
      )}

      {result.findings.length > 0 && (
        <div className="space-y-3">
          {result.findings.map((finding, i) => (
            <Surface key={i} tone="neutral" padding="md">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-ink">{finding.claim}</p>
                <Badge tone={STATUS_TONE[finding.status]}>{STATUS_LABEL[finding.status]}</Badge>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{finding.explanation}</p>
            </Surface>
          ))}
        </div>
      )}

      {(result.agreements.length > 0 || result.disagreements.length > 0) && (
        <div className="grid gap-3 sm:grid-cols-2">
          {result.agreements.length > 0 && (
            <Surface tone="neutral" padding="md">
              <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Where Sources Agree</p>
              <ul className="mt-2 space-y-1 text-sm text-ink-muted">
                {result.agreements.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </Surface>
          )}
          {result.disagreements.length > 0 && (
            <Surface tone="neutral" padding="md">
              <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Where Sources Disagree</p>
              <ul className="mt-2 space-y-1 text-sm text-ink-muted">
                {result.disagreements.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </Surface>
          )}
        </div>
      )}
    </div>
  );
}

export function SearchInvestigationScreen() {
  const { result, isInvestigating, error, investigate } = useSearchInvestigationContext();
  const [question, setQuestion] = useState("");

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Search Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Ask a real career question and Aureon investigates it across multiple trusted
        sources — acting like a research analyst, not a chatbot.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How Search Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Should I pursue AI Research?"
          className="w-full rounded-xl border border-border bg-surface px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/40 focus:outline-none"
        />
        <Button onClick={() => investigate(question)} disabled={isInvestigating || !question.trim()}>
          {isInvestigating ? "Investigating…" : "Investigate"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {!result && !isInvestigating && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={Search}
            title="No Investigation Yet"
            description="Ask a real career question above — Aureon will search trusted sources and build a Career Investigation Report."
          />
        </div>
      )}

      {result && result.status !== "completed" && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Complete This Investigation"
            description={result.explanation ?? "This question couldn't be investigated."}
          />
        </div>
      )}

      {result && result.status === "completed" && (
        <div className="mt-8">
          <MissionWorkspace
            snapshot={result.mission}
            artifactsUpdated={result.artifacts_updated}
            finalReport={investigationReport(result)}
          />
        </div>
      )}
    </div>
  );
}
