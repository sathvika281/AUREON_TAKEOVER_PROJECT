import { useState } from "react";
import { Link } from "react-router-dom";
import { Compass, FileStack, GitCompare, ListChecks, MessageSquareQuote, Route, ShieldAlert, Sprout } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { NextBestAction, type NextBestActionSuggestion } from "../../design-system/components/NextBestAction";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import type { CareerPathSimulation, CareerSimulation } from "../../shared/api/types";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { ComparisonMatrix } from "./ComparisonMatrix";
import { useDecisionContext } from "./DecisionContext";
import { DecisionJourneyHeader } from "./DecisionJourneyHeader";
import { DecisionMemoryList } from "./DecisionMemoryList";
import { DecisionTimeline } from "./DecisionTimeline";
import { DecisionWorkspaceCardDetail, DecisionWorkspaceCardSummary } from "./DecisionWorkspaceCard";

const MIN_SELECTION = 2;
const MAX_SELECTION = 4;

type Tab = "overview" | "compare" | "simulate";

/**
 * The Decision Workspace — one composed card per active career
 * candidate. Everything here is read from `DecisionContext.workspace`,
 * fetched once from `GET /decision-workspace`; this tab does no
 * composition of its own.
 */
function OverviewTab({ onCompare, onSimulate }: { onCompare: (careerId: string) => void; onSimulate: (careerId: string) => void }) {
  const { workspace, workspaceGaps } = useDecisionContext();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selected = workspace.find((c) => c.career_id === selectedId) ?? null;

  if (selected) {
    return (
      <DecisionWorkspaceCardDetail
        card={selected}
        onBack={() => setSelectedId(null)}
        onCompare={onCompare}
        onSimulate={onSimulate}
      />
    );
  }

  return (
    <div>
      {workspaceGaps.length > 0 && (
        <Surface tone="neutral" padding="md" className="mb-6">
          <p className="text-sm text-ink">You may want to explore these before making a final decision:</p>
          <ul className="mt-2 space-y-1">
            {workspaceGaps.map((g, i) => <li key={i} className="text-xs text-ink-muted">⚠ {g}</li>)}
          </ul>
        </Surface>
      )}

      {workspace.length === 0 ? (
        <EmptyStatePanel
          icon={Compass}
          title="No Career Candidates Yet"
          description="Analyze your fit in Career Explorer first — the Decision Workspace composes one card per real career candidate."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {workspace.map((card) => (
            <DecisionWorkspaceCardSummary key={card.career_id} card={card} onSelect={() => setSelectedId(card.career_id)} />
          ))}
        </div>
      )}

      <div className="mt-10 grid gap-8 sm:grid-cols-2">
        <div>
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Decision Memory</p>
          <DecisionMemoryList />
        </div>
        <div>
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Decision Timeline</p>
          <DecisionTimeline />
        </div>
      </div>
    </div>
  );
}

const HOW_COMPARISON_WORKS_STEPS = [
  {
    icon: FileStack,
    title: "Facts come from the Career Knowledge Base",
    description: "Work style, salary, education, lifestyle, and 11 other dimensions are read directly from real career data — never invented by the model.",
  },
  {
    icon: GitCompare,
    title: "Reasoning comes from your evidence",
    description: "Only the 'why it matters to you' line under each dimension is personalized, and only ever against evidence already in your Career DNA.",
  },
  {
    icon: MessageSquareQuote,
    title: "Missing evidence is named, not guessed",
    description: "When Aureon doesn't have enough to compare something meaningfully, it says so directly instead of filling the gap with a plausible-sounding answer.",
  },
];

const HOW_SIMULATION_WORKS_STEPS = [
  {
    icon: Route,
    title: "2-4 paths, independently simulated",
    description: "Each career path is reasoned about entirely on its own merits — never described relative to the others.",
  },
  {
    icon: Compass,
    title: "15 real dimensions per path",
    description: "Skills, education, environment, risk, and adaptability come straight from the Career Knowledge Base; alignment and evidence confidence come from your own real Career DNA and evidence, never a fresh guess.",
  },
  {
    icon: ListChecks,
    title: "Always ends with next steps",
    description: "Every path closes with real, concrete actions — never generic advice, always drawn from your actual investigations, mentors, and matches.",
  },
  {
    icon: ShieldAlert,
    title: "A picture, never a prediction",
    description: "This is one possible, evidence-informed journey — never a certainty, never a decision made for you.",
  },
];

const DIMENSION_LABELS: { key: keyof CareerPathSimulation; label: string }[] = [
  { key: "required_skills", label: "Required Skills" },
  { key: "higher_education_path", label: "Higher Education Path" },
  { key: "work_environment", label: "Work Environment" },
  { key: "lifestyle", label: "Lifestyle" },
  { key: "typical_challenges", label: "Typical Challenges" },
  { key: "growth_potential", label: "Growth Potential" },
  { key: "risk_factors", label: "Risk Factors" },
  { key: "research_opportunities", label: "Research Opportunities" },
  { key: "industry_opportunities", label: "Industry Opportunities" },
  { key: "future_adaptability", label: "Future Adaptability" },
  { key: "career_dna_alignment", label: "Career DNA Alignment" },
  { key: "student_interest_alignment", label: "Student Interest Alignment" },
  { key: "evidence_confidence", label: "Evidence Confidence" },
];

function ComparisonPlaceholderPanels() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {["Career A", "Career B"].map((slot) => (
        <Surface key={slot} tone="raised" padding="md" className="border-dashed">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{slot}</p>
          <p className="mt-2 text-sm text-ink-faint">Select a career candidate to fill this slot.</p>
        </Surface>
      ))}
    </div>
  );
}

function CompareTab({ initialCareerId }: { initialCareerId?: string | null }) {
  const { candidates } = useCareerIntelligenceContext();
  const { comparisons, isBusy, error, runComparison, recommendedColleges, recommendedExperts } = useDecisionContext();
  const [selected, setSelected] = useState<string[]>(() => (initialCareerId ? [initialCareerId] : []));

  const toggle = (careerId: string) => {
    setSelected((prev) => {
      if (prev.includes(careerId)) return prev.filter((id) => id !== careerId);
      if (prev.length >= MAX_SELECTION) return prev;
      return [...prev, careerId];
    });
  };

  const orderedComparisons = [...comparisons].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  if (candidates.length < MIN_SELECTION) {
    return (
      <div className="space-y-6">
        <ProcessSteps title="How Comparison Works" steps={HOW_COMPARISON_WORKS_STEPS} />
        <ComparisonPlaceholderPanels />
        <div className="flex items-start gap-3 border-l border-border-strong pl-4">
          <Sprout size={16} className="mt-0.5 shrink-0 text-accent-soft" />
          <p className="text-sm leading-relaxed text-ink-muted">
            Analyze your fit in Career Explorer first — comparing needs at least two career
            candidates to weigh against each other. You currently have {candidates.length}.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <ProcessSteps title="How Comparison Works" steps={HOW_COMPARISON_WORKS_STEPS} />
      </div>

      <p className="text-sm text-ink-muted">Pick 2–4 career candidates to compare.</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {candidates.map((c) => (
          <button
            key={c.career_id}
            onClick={() => toggle(c.career_id)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs transition-colors",
              selected.includes(c.career_id)
                ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
            )}
          >
            {c.career_name}
          </button>
        ))}
      </div>
      <div className="mt-4">
        <Button
          disabled={selected.length < MIN_SELECTION || isBusy}
          onClick={() => runComparison(selected)}
        >
          {isBusy ? "Comparing…" : "Compare"}
        </Button>
      </div>
      {error && <p className="mt-3 text-xs text-danger">{error}</p>}

      {orderedComparisons.length === 0 ? (
        <div className="mt-8">
          <ComparisonPlaceholderPanels />
        </div>
      ) : (
        <div className="mt-8 space-y-8">
          {orderedComparisons.map((comparison) => (
            <ComparisonMatrix key={comparison.id} comparison={comparison} />
          ))}
        </div>
      )}

      {(recommendedColleges.length > 0 || recommendedExperts.length > 0) && (
        <div className="mt-8">
          <Surface tone="neutral" padding="md">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
              Recommended in Career Exploration Ecosystem
            </p>
            <p className="mt-1 text-xs text-ink-faint">
              Real, deterministic pulls from your own Institution/Mentor Match analysis — never a
              new recommendation.
            </p>
            {recommendedColleges.length > 0 && (
              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                <span className="text-xs text-ink-muted">Colleges:</span>
                {recommendedColleges.map((name) => (
                  <Badge key={name} tone="warm">{name}</Badge>
                ))}
              </div>
            )}
            {recommendedExperts.length > 0 && (
              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                <span className="text-xs text-ink-muted">Experts:</span>
                {recommendedExperts.map((name) => (
                  <Badge key={name} tone="warm">{name}</Badge>
                ))}
              </div>
            )}
            <div className="mt-3 flex gap-4">
              <Link to="/experience/college-collaboration" className="text-xs text-accent-soft hover:text-accent">
                College Explorer →
              </Link>
              <Link to="/experience/expert-connect" className="text-xs text-accent-soft hover:text-accent">
                Expert Connect →
              </Link>
            </div>
          </Surface>
        </div>
      )}
    </div>
  );
}

/** A single simulated path — framed as a trajectory moving away from
 * "now," not a stacked feature card. The 15 dimensions read as waypoints
 * along that line; the illustrative journey is a real connected route,
 * not boxed milestone chips. */
function PathCard({ path, index, total }: { path: CareerPathSimulation; index: number; total: number }) {
  return (
    <Surface tone="raised" padding="lg">
      <div className="flex items-baseline justify-between gap-3">
        <p className="text-lg font-medium text-ink">{path.career_name}</p>
        <p className="font-mono text-[0.6rem] tracking-[0.14em] text-ink-faint">
          Path {index + 1} / {total}
        </p>
      </div>

      <div className="mt-5 grid gap-x-6 gap-y-3 sm:grid-cols-2">
        {DIMENSION_LABELS.map(({ key, label }) => (
          <div key={key} className="flex gap-2.5">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent-soft/50" />
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">{label}</p>
              <p className="mt-1 text-xs leading-relaxed text-ink-muted">{path[key] as string}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 border-t border-border pt-4">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Learning Journey</p>
        <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{path.learning_journey}</p>
      </div>

      <div className="mt-5">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
          Illustrative Journey
        </p>
        <div className="mt-3 space-y-3.5 border-l border-border pl-4">
          {path.timeline.map((phase, i) => (
            <div key={i} className="relative">
              <span className="absolute -left-[19px] top-1.5 h-1.5 w-1.5 rounded-full border border-accent-soft bg-canvas" />
              <p className="text-xs font-medium text-ink">
                {phase.phase} — {phase.focus}
              </p>
              <p className="mt-1 text-xs text-ink-faint">{phase.milestones.join(" · ")}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Advantages</p>
          <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.advantages.map((a, i) => <li key={i}>+ {a}</li>)}</ul>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Sacrifices</p>
          <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.sacrifices.map((s, i) => <li key={i}>– {s}</li>)}</ul>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Opportunities</p>
          <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.opportunities.map((o, i) => <li key={i}>+ {o}</li>)}</ul>
        </div>
        <div>
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Uncertainties</p>
          <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.uncertainties.map((u, i) => <li key={i}>? {u}</li>)}</ul>
        </div>
      </div>

      <div className="mt-5 border-t border-border pt-4">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">Next Best Actions</p>
        <ul className="mt-2 space-y-1 text-xs text-ink-muted">
          {path.next_best_actions.map((a, i) => <li key={i}>→ {a}</li>)}
        </ul>
      </div>
    </Surface>
  );
}

export function simulationReport(simulation: CareerSimulation) {
  const insights = simulation.decision_insights;
  return (
    <div className="space-y-6">
      {simulation.simulations.map((path, i) => (
        <PathCard key={path.career_id} path={path} index={i} total={simulation.simulations.length} />
      ))}

      <div className="border-t border-border pt-6">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
          AI Recommendation
        </p>
        {insights.strongest_match_career_id && (
          <p className="mt-3 text-sm text-ink">
            Strongest match:{" "}
            <span className="text-accent-soft">
              {simulation.career_names[insights.strongest_match_career_id]}
            </span>
          </p>
        )}
        <p className="mt-2 font-serif text-base italic leading-relaxed text-ink">{insights.why}</p>

        {insights.possible_risks.length > 0 && (
          <div className="mt-4">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Possible Risks</p>
            <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{insights.possible_risks.map((r, i) => <li key={i}>– {r}</li>)}</ul>
          </div>
        )}
        {insights.questions_to_explore.length > 0 && (
          <div className="mt-4">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">Questions to Explore</p>
            <ul className="mt-1.5 space-y-0.5 text-xs text-ink-muted">{insights.questions_to_explore.map((q, i) => <li key={i}>? {q}</li>)}</ul>
          </div>
        )}
        {insights.recommended_next_investigation && (
          <p className="mt-4 text-xs text-ink-muted"><span className="text-ink-faint">Recommended next: </span>{insights.recommended_next_investigation}</p>
        )}
        {(insights.recommended_mentors.length > 0 || insights.recommended_institutions.length > 0) && (
          <div className="mt-4 flex flex-wrap gap-2">
            {insights.recommended_mentors.map((m, i) => <Badge key={`m${i}`} tone="warm">Mentor: {m}</Badge>)}
            {insights.recommended_institutions.map((inst, i) => <Badge key={`i${i}`} tone="cool">Institution: {inst}</Badge>)}
          </div>
        )}
      </div>
    </div>
  );
}

function FutureSimulationTab({ initialCareerId }: { initialCareerId?: string | null }) {
  const { candidates } = useCareerIntelligenceContext();
  const {
    simulations, isBusy, error, runSimulation, simulationInsufficientReason,
    lastSimulationMission, lastSimulationArtifactsUpdated,
  } = useDecisionContext();
  const [selected, setSelected] = useState<string[]>(() => (initialCareerId ? [initialCareerId] : []));

  const toggle = (careerId: string) => {
    setSelected((prev) => {
      if (prev.includes(careerId)) return prev.filter((id) => id !== careerId);
      if (prev.length >= MAX_SELECTION) return prev;
      return [...prev, careerId];
    });
  };

  const latestSimulation = [...simulations].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];

  return (
    <div>
      <div className="mb-6">
        <ProcessSteps title="How Future Simulation Works" steps={HOW_SIMULATION_WORKS_STEPS} />
      </div>

      {candidates.length < MIN_SELECTION ? (
        <div className="flex items-start gap-3 border-l border-border-strong pl-4">
          <Sprout size={16} className="mt-0.5 shrink-0 text-accent-soft" />
          <p className="text-sm leading-relaxed text-ink-muted">
            Analyze your fit in Career Explorer first — simulating futures needs at least two
            career candidates. You currently have {candidates.length}.
          </p>
        </div>
      ) : (
        <>
          <p className="text-sm text-ink-muted">Pick 2 to 4 career candidates.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {candidates.map((c) => (
              <button
                key={c.career_id}
                onClick={() => toggle(c.career_id)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-xs transition-colors",
                  selected.includes(c.career_id)
                    ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                    : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
                )}
              >
                {c.career_name}
              </button>
            ))}
          </div>
          <div className="mt-4">
            <Button
              disabled={selected.length < MIN_SELECTION || selected.length > MAX_SELECTION || isBusy}
              onClick={() => runSimulation(selected)}
            >
              {isBusy ? "Simulating…" : "Simulate These Paths"}
            </Button>
          </div>
          {error && <p className="mt-3 text-xs text-danger">{error}</p>}
        </>
      )}

      {!latestSimulation && !simulationInsufficientReason && (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Route}
            title="No Simulation Yet"
            description="Select 2-4 of your career candidates above — Aureon will simulate each path independently and compare them."
          />
        </div>
      )}

      {simulationInsufficientReason && (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Complete This Simulation"
            description={simulationInsufficientReason}
          />
        </div>
      )}

      {latestSimulation && !simulationInsufficientReason && (
        <div className="mt-8">
          {lastSimulationMission ? (
            <MissionWorkspace
              snapshot={lastSimulationMission}
              artifactsUpdated={lastSimulationArtifactsUpdated}
              finalReport={simulationReport(latestSimulation)}
            />
          ) : (
            simulationReport(latestSimulation)
          )}
        </div>
      )}
    </div>
  );
}

function deriveNextBestAction(
  simulations: CareerSimulation[],
  comparisons: number,
): NextBestActionSuggestion {
  const latest = [...simulations].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];
  const strongestId = latest?.decision_insights.strongest_match_career_id;
  if (latest && strongestId) {
    return {
      action: `See ${latest.career_names[strongestId]} in Career Explorer`,
      reason: "Your strongest simulated match so far — worth a closer look at its real details.",
      to: `/explore/career-reality/${strongestId}`,
    };
  }
  if (comparisons === 0) {
    return {
      action: "Compare your career candidates",
      reason: "Decision Lab needs at least two real candidates to reason about — start with a comparison.",
    };
  }
  return {
    action: "Run a Future Simulation",
    reason: "You've compared careers — simulating a path shows what each one could realistically look like.",
  };
}

export function DecisionLabScreen() {
  const [tab, setTab] = useState<Tab>("overview");
  const [pendingCareerId, setPendingCareerId] = useState<string | null>(null);
  const { simulations, comparisons, stageProgress, overallReadinessPercent } = useDecisionContext();

  const goToCompare = (careerId: string) => {
    setPendingCareerId(careerId);
    setTab("compare");
  };
  const goToSimulate = (careerId: string) => {
    setPendingCareerId(careerId);
    setTab("simulate");
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Decision Lab</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Which path should I choose? Every difference explained against your own Career DNA and
        evidence — this is decision support, not a ranking.
      </p>

      <div className="mt-6">
        <DecisionJourneyHeader stageProgress={stageProgress} overallReadinessPercent={overallReadinessPercent} />
      </div>

      <div className="mt-2">
        <NextBestAction suggestion={deriveNextBestAction(simulations, comparisons.length)} />
      </div>

      <div className="mt-6 flex gap-2 border-b border-border">
        {([
          { id: "overview" as const, label: "Overview" },
          { id: "compare" as const, label: "Compare Careers" },
          { id: "simulate" as const, label: "Future Simulation" },
        ]).map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={cn(
              "px-3 py-2 text-sm transition-colors",
              tab === id ? "border-b-2 border-accent-soft text-ink" : "text-ink-faint hover:text-ink-muted",
            )}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "overview" && <OverviewTab onCompare={goToCompare} onSimulate={goToSimulate} />}
        {tab === "compare" && <CompareTab initialCareerId={pendingCareerId} />}
        {tab === "simulate" && <FutureSimulationTab initialCareerId={pendingCareerId} />}
      </div>
    </div>
  );
}
