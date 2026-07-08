import { useState } from "react";
import { Link } from "react-router-dom";
import { FileStack, GitCompare, MessageSquareQuote, Sprout } from "lucide-react";

import { cn } from "../../design-system/cn";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { ComparisonMatrix } from "./ComparisonMatrix";
import { useDecisionContext } from "./DecisionContext";
import { DecisionMemoryList } from "./DecisionMemoryList";
import { DecisionTimeline } from "./DecisionTimeline";

const MIN_SELECTION = 2;
const MAX_SELECTION = 4;

type Tab = "compare" | "timeline" | "memory";

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

function ComparisonPlaceholderPanels() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {["Career A", "Career B"].map((slot) => (
        <Surface key={slot} tone="raised" padding="md" className="border-dashed">
          <p className="text-xs uppercase tracking-widest text-ink-faint">{slot}</p>
          <p className="mt-2 text-sm text-ink-faint">Select a career candidate to fill this slot.</p>
        </Surface>
      ))}
    </div>
  );
}

function CompareTab() {
  const { candidates } = useCareerIntelligenceContext();
  const { comparisons, isBusy, error, runComparison, recommendedColleges, recommendedExperts } = useDecisionContext();
  const [selected, setSelected] = useState<string[]>([]);

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
        <Surface tone="neutral" padding="md" className="flex items-start gap-3">
          <Sprout size={16} className="mt-0.5 shrink-0 text-accent-soft" />
          <p className="text-sm leading-relaxed text-ink-muted">
            Analyze your fit in Career Intelligence first — comparing needs at least two career
            candidates to weigh against each other. You currently have {candidates.length}.
          </p>
        </Surface>
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
          disabled={selected.length < MIN_SELECTION || isBusy}
          onClick={() => runComparison(selected)}
        >
          {isBusy ? "Comparing…" : "Compare"}
        </Button>
      </div>
      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

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
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
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
                College Collaboration →
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

export function DecisionLabScreen() {
  const [tab, setTab] = useState<Tab>("compare");

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Decision Lab</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Aureon's comparison engine — every difference explained against your own Career DNA and
        evidence. This is decision support, not a ranking.
      </p>

      <div className="mt-6 flex gap-2 border-b border-border">
        {(["compare", "timeline", "memory"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "px-3 py-2 text-sm capitalize transition",
              tab === t ? "border-b-2 border-accent text-ink" : "text-ink-faint hover:text-ink-muted",
            )}
          >
            {t === "memory" ? "Decision Memory" : t}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "compare" && <CompareTab />}
        {tab === "timeline" && <DecisionTimeline />}
        {tab === "memory" && <DecisionMemoryList />}
      </div>
    </div>
  );
}
