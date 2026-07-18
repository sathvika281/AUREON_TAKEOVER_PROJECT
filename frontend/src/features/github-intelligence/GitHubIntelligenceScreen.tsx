import { useState } from "react";
import { Code2, GitBranch, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Field } from "../../design-system/components/Field";
import { Input } from "../../design-system/components/Input";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import type { GitHubInvestigationResult } from "../../shared/api/types";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useGitHubIntelligenceContext } from "./GitHubIntelligenceContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: GitBranch,
    title: "Reads the real repository",
    description: "Genuine GitHub API data — metadata, languages, README, file structure — never a scrape, never a guess.",
  },
  {
    icon: Code2,
    title: "Evaluates what you built, not what you claim",
    description: "Structure, technologies, dependencies, build configuration, documentation, tests, and CI — real signals only.",
  },
  {
    icon: Sparkles,
    title: "Never judges by popularity",
    description: "Stars and forks are shown as metadata, but never influence the engineering analysis or your Career DNA.",
  },
  {
    icon: ShieldAlert,
    title: "Explains itself honestly",
    description: "Private, missing, or rate-limited repositories get a clear explanation — never fabricated findings.",
  },
];

const ANALYSIS_LABELS: { key: keyof GitHubInvestigationResult; label: string }[] = [
  { key: "project_purpose", label: "Project Purpose" },
  { key: "technical_complexity", label: "Technical Complexity" },
  { key: "problem_solving", label: "Problem Solving" },
  { key: "code_organization", label: "Code Organization" },
  { key: "technology_breadth", label: "Technology Breadth" },
  { key: "documentation_quality", label: "Documentation Quality" },
  { key: "learning_signals", label: "Learning Signals" },
  { key: "engineering_maturity", label: "Engineering Maturity" },
  { key: "research_orientation", label: "Research Orientation" },
  { key: "ai_ml_signals", label: "AI/ML Signals" },
];

export function engineeringReport(result: GitHubInvestigationResult) {
  return (
    <div className="space-y-4">
      {result.repo && (
        <Surface tone="raised" padding="md">
          <div className="flex items-baseline justify-between">
            <p className="text-sm font-medium text-ink">{result.repo.owner}/{result.repo.name}</p>
            <div className="flex gap-2 text-xs text-ink-faint">
              <span>★ {result.repo.stars}</span>
              <span>⑂ {result.repo.forks}</span>
            </div>
          </div>
          {result.repo.description && (
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">{result.repo.description}</p>
          )}
          <p className="mt-2 text-xs text-ink-faint">
            {result.repo.primary_language ?? "Unknown language"}
            {result.repo.license ? ` · ${result.repo.license}` : ""}
          </p>
        </Surface>
      )}

      {result.overall_summary && (
        <Surface tone="neutral" padding="md">
          <p className="text-sm leading-relaxed text-ink">{result.overall_summary}</p>
        </Surface>
      )}

      {result.skills.length > 0 && (
        <Surface tone="neutral" padding="md">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Skills Demonstrated</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {result.skills.map((s, i) => (
              <Badge key={i} tone="warm">{s.category}: {s.skill}</Badge>
            ))}
          </div>
        </Surface>
      )}

      <Field divided>
        {ANALYSIS_LABELS.map(({ key, label }) => {
          const value = result[key];
          if (!value || typeof value !== "string") return null;
          return (
            <div key={key} className="py-3 first:pt-0 last:pb-0">
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">{label}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{value}</p>
            </div>
          );
        })}
      </Field>
    </div>
  );
}

export function GitHubIntelligenceScreen() {
  const { result, isInvestigating, error, investigate } = useGitHubIntelligenceContext();
  const [url, setUrl] = useState("");

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">GitHub Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Submit a public GitHub repository and Aureon investigates it as a real engineering
        mission — evaluating what you've actually built, not what you claim.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How GitHub Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
        />
        <Button onClick={() => investigate(url)} disabled={isInvestigating || !url.trim()}>
          {isInvestigating ? "Investigating…" : "Investigate"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-danger">{error}</p>}

      {!result && !isInvestigating && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={GitBranch}
            title="No Repository Investigated Yet"
            description="Paste a public GitHub repository URL above — Aureon will read it and build a real Engineering Intelligence Report."
          />
        </div>
      )}

      {result && result.status !== "completed" && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Complete This Investigation"
            description={result.explanation ?? "This repository couldn't be investigated."}
          />
        </div>
      )}

      {result && result.status === "completed" && (
        <div className="mt-8">
          <MissionWorkspace
            snapshot={result.mission}
            artifactsUpdated={result.artifacts_updated}
            finalReport={engineeringReport(result)}
          />
        </div>
      )}
    </div>
  );
}
