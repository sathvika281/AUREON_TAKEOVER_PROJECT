import { useState } from "react";
import { Compass, ListChecks, Route, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import type { CareerPathSimulation, CareerSimulation } from "../../shared/api/types";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { useDecisionContext } from "./DecisionContext";

const MIN_SELECTION = 2;
const MAX_SELECTION = 4;

const HOW_IT_WORKS_STEPS = [
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
    title: "A laboratory, never a prediction",
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

function PathCard({ path }: { path: CareerPathSimulation }) {
  return (
    <Surface tone="raised" padding="md">
      <p className="text-base font-medium text-ink">{path.career_name}</p>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {DIMENSION_LABELS.map(({ key, label }) => (
          <div key={key}>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{label}</p>
            <p className="mt-1 text-xs leading-relaxed text-ink-muted">{path[key] as string}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 border-t border-border pt-3">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Learning Journey</p>
        <p className="mt-1 text-sm leading-relaxed text-ink-muted">{path.learning_journey}</p>
      </div>

      <div className="mt-4">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Illustrative Journey</p>
        <div className="mt-2 space-y-2">
          {path.timeline.map((phase, i) => (
            <div key={i} className="rounded-lg bg-white/[0.03] px-3 py-2">
              <p className="text-xs font-medium text-ink">{phase.phase} — {phase.focus}</p>
              <p className="mt-1 text-xs text-ink-faint">{phase.milestones.join(" · ")}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Advantages</p>
          <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.advantages.map((a, i) => <li key={i}>+ {a}</li>)}</ul>
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Sacrifices</p>
          <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.sacrifices.map((s, i) => <li key={i}>– {s}</li>)}</ul>
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Opportunities</p>
          <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.opportunities.map((o, i) => <li key={i}>+ {o}</li>)}</ul>
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Uncertainties</p>
          <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{path.trade_offs.uncertainties.map((u, i) => <li key={i}>? {u}</li>)}</ul>
        </div>
      </div>

      <div className="mt-4 border-t border-border pt-3">
        <p className="text-[0.65rem] uppercase tracking-widest text-accent-soft">Next Best Actions</p>
        <ul className="mt-1.5 space-y-1 text-xs text-ink-muted">
          {path.next_best_actions.map((a, i) => <li key={i}>→ {a}</li>)}
        </ul>
      </div>
    </Surface>
  );
}

export function simulationReport(simulation: CareerSimulation) {
  const insights = simulation.decision_insights;
  return (
    <div className="space-y-4">
      {simulation.simulations.map((path) => <PathCard key={path.career_id} path={path} />)}

      <Surface tone="neutral" padding="md">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Decision Insights</p>
        {insights.strongest_match_career_id && (
          <p className="mt-2 text-sm text-ink">
            Strongest match: <span className="text-accent-soft">{simulation.career_names[insights.strongest_match_career_id]}</span>
          </p>
        )}
        <p className="mt-1 text-sm leading-relaxed text-ink-muted">{insights.why}</p>

        {insights.possible_risks.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Possible Risks</p>
            <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{insights.possible_risks.map((r, i) => <li key={i}>– {r}</li>)}</ul>
          </div>
        )}
        {insights.questions_to_explore.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Questions to Explore</p>
            <ul className="mt-1 space-y-0.5 text-xs text-ink-muted">{insights.questions_to_explore.map((q, i) => <li key={i}>? {q}</li>)}</ul>
          </div>
        )}
        {insights.recommended_next_investigation && (
          <p className="mt-3 text-xs text-ink-muted"><span className="text-ink-faint">Recommended next: </span>{insights.recommended_next_investigation}</p>
        )}
        {(insights.recommended_mentors.length > 0 || insights.recommended_institutions.length > 0) && (
          <div className="mt-3 flex flex-wrap gap-2">
            {insights.recommended_mentors.map((m, i) => <Badge key={`m${i}`} tone="warm">Mentor: {m}</Badge>)}
            {insights.recommended_institutions.map((inst, i) => <Badge key={`i${i}`} tone="cool">Institution: {inst}</Badge>)}
          </div>
        )}
      </Surface>
    </div>
  );
}

export function CareerSimulatorScreen() {
  const { candidates } = useCareerIntelligenceContext();
  const {
    simulations, isBusy, error, runSimulation, simulationInsufficientReason,
    lastSimulationMission, lastSimulationArtifactsUpdated,
  } = useDecisionContext();
  const [selected, setSelected] = useState<string[]>([]);

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
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Career Simulator</h1>
      <p className="mt-2 text-sm text-ink-muted">
        A Decision Laboratory, not a prediction engine — explore what 2-4 possible career paths
        could realistically look like, grounded in your own evidence.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How the Career Simulator Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      {candidates.length < MIN_SELECTION ? (
        <div className="mt-6">
          <Surface tone="neutral" padding="md" className="flex items-start gap-3">
            <Sparkles size={16} className="mt-0.5 shrink-0 text-accent-soft" />
            <p className="text-sm leading-relaxed text-ink-muted">
              Analyze your fit in Career Intelligence first — simulating futures needs at least two
              career candidates. You currently have {candidates.length}.
            </p>
          </Surface>
        </div>
      ) : (
        <>
          <p className="mt-6 text-sm text-ink-muted">Pick 2 to 4 career candidates.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {candidates.map((c) => (
              <button
                key={c.career_id}
                onClick={() => toggle(c.career_id)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-xs transition",
                  selected.includes(c.career_id)
                    ? "border-accent/40 bg-accent/10 text-accent-soft"
                    : "border-border text-ink-faint hover:text-ink-muted",
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
          {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
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
