import { useState } from "react";
import { CheckCircle2, Search, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Field } from "../../design-system/components/Field";
import { Input } from "../../design-system/components/Input";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import type { Finding, SearchInvestigationResult } from "../../shared/api/types";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useSearchInvestigationContext } from "./SearchInvestigationContext";

/** A signal-strength reading, not a checkmark badge — how strongly a
 * source came through, echoing the observatory's instrument vocabulary. */
function SignalBars({ reached }: { reached: boolean }) {
  return (
    <span className="flex items-end gap-0.5" aria-hidden="true">
      {[3, 5, 7].map((h, i) => (
        <span
          key={i}
          className={cn("w-[3px] rounded-full", reached ? "bg-accent-soft" : "bg-ink-faint/25")}
          style={{ height: h }}
        />
      ))}
    </span>
  );
}

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
    <div className="space-y-8">
      {result.source_availability && (
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            Signal — {result.source_availability.sources_retrieved}/
            {result.source_availability.total_sources} sources reached
          </p>
          <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2">
            {result.source_availability.sources.map((s) => (
              <div key={s.name} className="flex items-center gap-2 text-sm text-ink-muted">
                <SignalBars reached={s.reached} />
                <span>{s.name}</span>
                {s.note && <span className="text-xs text-ink-faint">({s.note})</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {result.overall_summary && (
        <p className="font-serif text-lg italic leading-relaxed text-ink">{result.overall_summary}</p>
      )}

      {result.findings.length > 0 && (
        <Field divided>
          {result.findings.map((finding, i) => (
            <div key={i} className="py-4 first:pt-0 last:pb-0">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-ink">{finding.claim}</p>
                <Badge tone={STATUS_TONE[finding.status]}>{STATUS_LABEL[finding.status]}</Badge>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{finding.explanation}</p>
            </div>
          ))}
        </Field>
      )}

      {(result.agreements.length > 0 || result.disagreements.length > 0) && (
        <div className="grid gap-8 sm:grid-cols-2">
          {result.agreements.length > 0 && (
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Where Sources Agree
              </p>
              <ul className="mt-3 space-y-2.5 text-sm text-ink-muted">
                {result.agreements.map((a, i) => (
                  <li key={i} className="border-l border-accent/30 pl-3">{a}</li>
                ))}
              </ul>
            </div>
          )}
          {result.disagreements.length > 0 && (
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Where Sources Disagree
              </p>
              <ul className="mt-3 space-y-2.5 text-sm text-ink-muted">
                {result.disagreements.map((d, i) => (
                  <li key={i} className="border-l border-border-strong pl-3">{d}</li>
                ))}
              </ul>
            </div>
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
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">
        The Deep Space Telescope
      </p>
      <h1 className="mt-2 text-2xl font-light text-ink">Search Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Ask a real career question and Aureon investigates it across multiple trusted
        sources — acting like a research analyst, not a chatbot.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How Search Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Should I pursue AI Research?"
        />
        <Button onClick={() => investigate(question)} disabled={isInvestigating || !question.trim()}>
          {isInvestigating ? "Investigating…" : "Investigate"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-danger">{error}</p>}

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
