import { useState } from "react";
import { Compass, Orbit, ShieldAlert, Sprout } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { useDecisionContext } from "./DecisionContext";

const REQUIRED_SELECTION = 2;

const HOW_IT_WORKS_STEPS = [
  {
    icon: Orbit,
    title: "Two careers, side by side",
    description: "Pick exactly two of your career candidates — each becomes one side of the simulation.",
  },
  {
    icon: Compass,
    title: "Five real dimensions, per side",
    description: "Daily work, lifestyle, growth, challenges, and future opportunities — read from each career's real profile, not invented for the comparison.",
  },
  {
    icon: ShieldAlert,
    title: "A picture, never a prediction",
    description: "Framed explicitly as one possible path based on your current evidence — not a forecast of what will actually happen.",
  },
];

const PLACEHOLDER_FIELDS = [
  { key: "daily_work", label: "Daily work" },
  { key: "lifestyle", label: "Lifestyle" },
  { key: "growth", label: "Growth" },
  { key: "challenges", label: "Challenges" },
  { key: "future_opportunities", label: "Future opportunities" },
];

function UniversePlaceholderPanels() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {["Universe A", "Universe B"].map((slot) => (
        <Surface key={slot} tone="raised" padding="md" className="border-dashed">
          <p className="text-sm font-medium text-ink-faint">{slot}</p>
          <div className="mt-3 space-y-2 text-xs leading-relaxed text-ink-faint">
            {PLACEHOLDER_FIELDS.map((field) => (
              <p key={field.key}>
                <span>{field.label}: </span>—
              </p>
            ))}
          </div>
        </Surface>
      ))}
    </div>
  );
}

export function ParallelUniverseScreen() {
  const { candidates } = useCareerIntelligenceContext();
  const { scenarios, isBusy, error, runParallelUniverse } = useDecisionContext();
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (careerId: string) => {
    setSelected((prev) => {
      if (prev.includes(careerId)) return prev.filter((id) => id !== careerId);
      if (prev.length >= REQUIRED_SELECTION) return [prev[1], careerId];
      return [...prev, careerId];
    });
  };

  const latestScenario = [...scenarios].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Parallel Universe</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Two possible futures, side by side — grounded in your real evidence, never a prediction.
      </p>

      <div className="mt-8">
        <ProcessSteps title="How Parallel Universe Works" steps={HOW_IT_WORKS_STEPS} />
      </div>

      {candidates.length < REQUIRED_SELECTION ? (
        <div className="mt-6">
          <Surface tone="neutral" padding="md" className="flex items-start gap-3">
            <Sprout size={16} className="mt-0.5 shrink-0 text-accent-soft" />
            <p className="text-sm leading-relaxed text-ink-muted">
              Analyze your fit in Career Intelligence first — simulating futures needs exactly two
              career candidates. You currently have {candidates.length}.
            </p>
          </Surface>
        </div>
      ) : (
        <>
          <p className="mt-6 text-sm text-ink-muted">Pick exactly two career candidates.</p>
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
              disabled={selected.length !== REQUIRED_SELECTION || isBusy}
              onClick={() => runParallelUniverse(selected)}
            >
              {isBusy ? "Simulating…" : "Simulate Futures"}
            </Button>
          </div>
          {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
        </>
      )}

      <div className="mt-8">
        {!latestScenario ? (
          <UniversePlaceholderPanels />
        ) : (
          <>
            <p className="rounded-lg bg-white/[0.03] px-3 py-2 text-xs italic text-ink-muted">
              {latestScenario.framing_note}
            </p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {latestScenario.branches.map((branch) => (
                <Surface key={branch.career_id} tone="raised" padding="md">
                  <p className="text-sm font-medium text-ink">{branch.career_name}</p>
                  <div className="mt-3 space-y-2 text-xs leading-relaxed text-ink-muted">
                    <p><span className="text-ink-faint">Daily work: </span>{branch.daily_work}</p>
                    <p><span className="text-ink-faint">Lifestyle: </span>{branch.lifestyle}</p>
                    <p><span className="text-ink-faint">Growth: </span>{branch.growth}</p>
                    <p><span className="text-ink-faint">Challenges: </span>{branch.challenges}</p>
                    <p><span className="text-ink-faint">Future opportunities: </span>{branch.future_opportunities}</p>
                  </div>
                </Surface>
              ))}
            </div>
            {latestScenario.missing_evidence.length > 0 && (
              <div className="mt-4">
                <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Missing evidence</p>
                <ul className="mt-1.5 space-y-0.5">
                  {latestScenario.missing_evidence.map((item, i) => (
                    <li key={i} className="text-xs text-ink-faint"><span>–</span> {item}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
