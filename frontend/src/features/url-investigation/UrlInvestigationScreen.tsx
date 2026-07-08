import { useState } from "react";
import { FileSearch, GitBranch, Globe, ShieldAlert } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useUrlInvestigationContext } from "./UrlInvestigationContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: Globe,
    title: "Fetches the real page",
    description: "A genuine HTTP request to the URL you paste — never simulated, never guessed at.",
  },
  {
    icon: FileSearch,
    title: "Extracts only real readable text",
    description: "Navigation, scripts, and styling are stripped out; only actual page content is kept.",
  },
  {
    icon: GitBranch,
    title: "Routes to the right specialist",
    description: "A GitHub repo goes to Discovery, a university page to Institution, a LinkedIn profile to Mentor — automatically, based on the URL itself.",
  },
  {
    icon: ShieldAlert,
    title: "Explains itself honestly",
    description: "If a page can't be read (paywalled, blocked, unavailable), Aureon says so directly rather than inventing findings.",
  },
];

function findingsReport({
  title, summary, keyFindings, structuredFields,
}: {
  title: string | null;
  summary: string | null;
  keyFindings: string[];
  structuredFields: Record<string, string>;
}) {
  return (
    <Surface tone="raised" padding="md">
      {title && <p className="text-sm font-medium text-ink">{title}</p>}
      {summary && <p className="mt-2 text-sm leading-relaxed text-ink-muted">{summary}</p>}
      {keyFindings.length > 0 && (
        <ul className="mt-3 space-y-1">
          {keyFindings.map((finding, i) => (
            <li key={i} className="text-xs text-ink-muted"><span className="text-accent">＋</span> {finding}</li>
          ))}
        </ul>
      )}
      {Object.entries(structuredFields).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border pt-3">
          {Object.entries(structuredFields).map(([key, value]) => (
            <span key={key} className="rounded-full border border-border px-2 py-1 text-[0.68rem] text-ink-faint">
              {key.replace(/_/g, " ")}: {value}
            </span>
          ))}
        </div>
      )}
    </Surface>
  );
}

export function UrlInvestigationScreen() {
  const { result, isInvestigating, error, investigate } = useUrlInvestigationContext();
  const [url, setUrl] = useState("");

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">URL Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Paste a career-related URL — a job article, a GitHub project, a university page, a
        mentor's profile — and Aureon investigates it as a real mission, routing to whichever
        specialist actually owns that kind of page.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How URL Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://…"
          className="w-full rounded-xl border border-border bg-surface px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/40 focus:outline-none"
        />
        <Button onClick={() => investigate(url)} disabled={isInvestigating || !url.trim()}>
          {isInvestigating ? "Investigating…" : "Investigate"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {!result && !isInvestigating && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={Globe}
            title="No Investigation Run Yet"
            description="Paste a URL above and Aureon will fetch it, classify it, and route it to the specialist who owns that kind of page."
          />
        </div>
      )}

      {result && result.status !== "completed" && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Complete This Investigation"
            description={result.explanation ?? "This page couldn't be read."}
          />
        </div>
      )}

      {result && result.status === "completed" && (
        <div className="mt-8">
          <MissionWorkspace
            snapshot={result.mission}
            artifactsUpdated={result.artifacts_updated}
            finalReport={findingsReport({
              title: result.title, summary: result.summary,
              keyFindings: result.key_findings, structuredFields: result.structured_fields,
            })}
          />
        </div>
      )}
    </div>
  );
}
