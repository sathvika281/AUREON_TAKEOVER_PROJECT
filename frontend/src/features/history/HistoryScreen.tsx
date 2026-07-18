import { useState } from "react";
import { Clock, GitCompareArrows, ShieldAlert } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import type { GitHubInvestigationResult, HistoryItem, MissionSnapshot } from "../../shared/api/types";
import { findingsReport } from "../document-intelligence/DocumentIntelligenceScreen";
import { CollegeMatchCard } from "../decision/CollegeMatchCard";
import { simulationReport } from "../decision/DecisionLabScreen";
import { MentorMatchCard } from "../decision/MentorMatchCard";
import { useDecisionContext } from "../decision/DecisionContext";
import { engineeringReport } from "../github-intelligence/GitHubIntelligenceScreen";
import { useHistoryContext } from "./HistoryContext";

const MISSION_TYPE_LABELS: Record<string, string> = {
  career_comparison: "Career Comparison",
  parallel_universe: "Parallel Universe",
  search_investigation: "Search Intelligence",
  career_simulation: "Career Simulation",
  github_investigation: "GitHub Investigation",
  document_investigation: "Document Analysis",
  mentor_match: "Guiding Stars",
  institution_match: "Nearby Worlds",
};

const EMPTY_MISSION: MissionSnapshot = { stages: [], agents: [], delegations: [], tools: [], evidence: [], narration: [] };

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}

/** Real elapsed time between two consecutive missions, mapped to real
 * visual spacing on the trail — dense where a lot happened close
 * together, sparse where a long stretch passed with nothing. Never a
 * fabricated density signal, only actual timestamp deltas. */
function gapForDelta(deltaMs: number): number {
  if (deltaMs <= 0) return 10;
  const hours = deltaMs / 3_600_000;
  return Math.min(44, 10 + Math.log2(1 + hours) * 7);
}

export function HistoryScreen() {
  const { items, githubInvestigations, documentInvestigations, searchInvestigations, isLoading } = useHistoryContext();
  const { comparisons, simulations, mentorMatches, collegeMatches } = useDecisionContext();
  const [selected, setSelected] = useState<HistoryItem | null>(null);

  function renderReport(item: HistoryItem) {
    switch (item.mission_type) {
      case "github_investigation": {
        const r = githubInvestigations.find((g) => g.id === item.artifact_id);
        if (!r) return null;
        const asResult: GitHubInvestigationResult = {
          url: r.url, status: "completed", explanation: null,
          repo: {
            name: r.name, description: r.description, owner: r.owner, primary_language: r.primary_language,
            languages: r.languages, topics: r.topics, license: r.license, stars: r.stars, forks: r.forks,
            last_activity: r.last_activity,
          },
          skills: r.skills, overall_summary: r.overall_summary, project_purpose: r.project_purpose,
          technical_complexity: r.technical_complexity, problem_solving: r.problem_solving,
          code_organization: r.code_organization, technology_breadth: r.technology_breadth,
          documentation_quality: r.documentation_quality, learning_signals: r.learning_signals,
          engineering_maturity: r.engineering_maturity, research_orientation: r.research_orientation,
          ai_ml_signals: r.ai_ml_signals, stages: [], evidence_added: true, mission: EMPTY_MISSION, artifacts_updated: [],
        };
        return engineeringReport(asResult);
      }
      case "document_investigation": {
        const r = documentInvestigations.find((d) => d.id === item.artifact_id);
        if (!r) return null;
        return findingsReport({
          title: r.title, summary: r.summary, keyFindings: r.key_findings, structuredFields: r.structured_fields,
        });
      }
      case "career_simulation": {
        const sim = simulations.find((s) => s.id === item.artifact_id);
        return sim ? simulationReport(sim) : null;
      }
      case "mentor_match": {
        const m = mentorMatches.find((mm) => mm.mentor_id === item.artifact_id);
        return m ? <MentorMatchCard match={m} /> : null;
      }
      case "institution_match": {
        const m = collegeMatches.find((cm) => cm.institution_id === item.artifact_id);
        return m ? <CollegeMatchCard match={m} /> : null;
      }
      case "search_investigation": {
        const inv = searchInvestigations.find((s) => s.id === item.artifact_id);
        if (!inv) return null;
        return (
          <Surface tone="raised" padding="md">
            <p className="text-sm leading-relaxed text-ink">{inv.overall_summary}</p>
            <div className="mt-3 space-y-3 border-l border-border pl-3">
              {inv.findings.map((f, i) => (
                <div key={i}>
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-medium text-ink">{f.claim}</p>
                    <Badge tone="cool">{f.status}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-ink-muted">{f.explanation}</p>
                </div>
              ))}
            </div>
          </Surface>
        );
      }
      case "career_comparison": {
        const c = comparisons.find((cc) => cc.id === item.artifact_id);
        if (!c) return null;
        return (
          <Surface tone="raised" padding="md">
            <p className="text-sm text-ink">{c.summary_reason}</p>
            <div className="mt-3 space-y-3 border-l border-border pl-3">
              {c.dimensions.map((d, i) => (
                <div key={i}>
                  <p className="text-xs font-medium text-ink">{d.dimension.replace(/_/g, " ")}</p>
                  <p className="mt-1 text-xs text-ink-muted">{d.why_it_matters_to_you}</p>
                </div>
              ))}
            </div>
          </Surface>
        );
      }
      default:
        return null;
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">The Wake</p>
      <h1 className="mt-2 text-2xl font-light text-ink">Journey Timeline</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Every real investigation, comparison, simulation, and match Aureon has run for you —
        select one to reopen its stored report, never regenerated.
      </p>

      {!isLoading && items.length === 0 && (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Clock}
            title="No History Yet"
            description="Run an investigation anywhere in Aureon — it will appear here, ready to reopen any time."
          />
        </div>
      )}

      <div className="mt-8 grid gap-8 sm:grid-cols-[280px_1fr]">
        <div className="border-l border-border pl-5">
          {items.map((item, i) => {
            const prev = items[i - 1];
            const marginTop =
              i === 0
                ? 0
                : gapForDelta(
                    Math.abs(new Date(prev.timestamp).getTime() - new Date(item.timestamp).getTime()),
                  );
            const isSelected = selected?.id === item.id;
            return (
              <button
                key={`${item.mission_type}:${item.id}`}
                onClick={() => setSelected(item)}
                style={{ marginTop }}
                className="relative block w-full text-left"
              >
                <span
                  className={`absolute -left-[23px] top-1.5 h-1.5 w-1.5 rounded-full border transition-colors ${
                    isSelected ? "border-accent-soft bg-accent-soft" : "border-border-strong bg-canvas"
                  }`}
                />
                <p className={`truncate text-sm transition-colors ${isSelected ? "text-ink" : "text-ink-muted"}`}>
                  {item.mission_name}
                </p>
                <div className="mt-1 flex items-center gap-2 font-mono text-[0.62rem] tracking-wide text-ink-faint">
                  <span>{MISSION_TYPE_LABELS[item.mission_type] ?? item.mission_type}</span>
                  <span>·</span>
                  <span>{formatTimestamp(item.timestamp)}</span>
                </div>
              </button>
            );
          })}
        </div>

        <div>
          {!selected ? (
            <div className="flex items-start gap-3 border-l border-border-strong pl-4">
              <GitCompareArrows size={16} className="mt-0.5 shrink-0 text-accent-soft" />
              <p className="text-sm text-ink-muted">Select an item on the left to reopen its stored report.</p>
            </div>
          ) : (
            <>
              <div className="mb-3 flex items-center gap-2">
                <Badge tone="warm">{MISSION_TYPE_LABELS[selected.mission_type] ?? selected.mission_type}</Badge>
                <span className="text-xs text-ink-faint">{selected.owning_specialist}</span>
              </div>
              {renderReport(selected) ?? (
                <EmptyStatePanel
                  icon={ShieldAlert}
                  title="Couldn't Load This Report"
                  description="The underlying record couldn't be found — try refreshing."
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
