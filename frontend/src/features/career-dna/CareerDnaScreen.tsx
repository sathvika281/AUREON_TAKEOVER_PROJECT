import { Link } from "react-router-dom";
import { Compass, Layers, MessagesSquare, ScanSearch, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Field } from "../../design-system/components/Field";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { UniverseSummaryCard } from "../discovery/components/UniverseSummaryCard";
import { UniverseWorkspaceTabs } from "../discovery/components/UniverseWorkspaceTabs";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { traitLabel } from "../discovery/network/layoutTraits";
import { BeliefRevisionEntry } from "../discovery/notebook/BeliefRevisionEntry";
import { ObservationEntry } from "../discovery/notebook/ObservationEntry";

function qualitativeLabel(score: number | null): string {
  if (score === null) return "Supported by evidence";
  if (score >= 0.7) return "Very Strong";
  if (score >= 0.4) return "Growing";
  if (score >= 0.15) return "Emerging";
  return "Still Exploring";
}

const FORMATION_STEPS = [
  {
    icon: MessagesSquare,
    title: "You talk, Aureon listens",
    description: "Every conversation in Identity Discovery is read for real signals — interests, working styles, values, and reactions — not a one-time quiz.",
  },
  {
    icon: ScanSearch,
    title: "Signals become evidence",
    description: "A signal only counts once it's specific enough to write down. Vague small talk doesn't move your Career DNA; concrete detail does.",
  },
  {
    icon: Layers,
    title: "Evidence accumulates into traits",
    description: "As evidence for the same trait repeats or deepens, its strength grows — from Still Exploring, to Emerging, to Growing, to Very Strong.",
  },
  {
    icon: Sparkles,
    title: "Aureon can change its mind",
    description: "New evidence can revise an earlier belief. When that happens, it's recorded as a belief revision, not silently overwritten.",
  },
];

/** Full Career DNA breakdown — never a percentage, every trait explains
 * why Aureon currently believes it, via the trait's own summary text. */
export function CareerDnaScreen() {
  const { careerDna, hypotheses, notebookEntries, confidenceScore, understandingStage } = useDiscoveryContext();
  const traits = Object.entries(careerDna);

  const evidenceTimeline = [...notebookEntries]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="mb-8 space-y-4">
        <UniverseSummaryCard
          hypotheses={hypotheses}
          careerDna={careerDna}
          confidenceScore={confidenceScore}
          understandingStage={understandingStage}
        />
        <UniverseWorkspaceTabs />
      </div>

      <h1 className="text-2xl font-light text-ink">Career DNA</h1>
      <p className="mt-2 text-sm text-ink-muted">
        A living profile, built from evidence rather than a one-time quiz result.
      </p>

      {/* Current Evidence Summary + Confidence Progress */}
      <div className="mt-8">
        <Surface tone="neutral" padding="md">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Confidence Progress</p>
            <Badge tone="warm">{understandingStage}</Badge>
          </div>
          <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out"
              style={{ width: `${Math.round(confidenceScore * 100)}%` }}
            />
          </div>
          <div className="mt-4 flex gap-8 border-t border-border pt-4">
            <div>
              <p className="text-lg font-light text-ink">{traits.length}</p>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">Traits tracked</p>
            </div>
            <div>
              <p className="text-lg font-light text-ink">{notebookEntries.length}</p>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">Evidence entries</p>
            </div>
          </div>
        </Surface>
      </div>

      {/* Traits Being Built */}
      <div className="mt-8">
        <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Traits Being Built</p>
        {traits.length === 0 ? (
          <EmptyStatePanel
            icon={Compass}
            title="Waiting for your first signals"
            description="Nothing has been evidenced yet. Traits appear here the moment a conversation gives Aureon something specific to work with."
            action={
              <Link
                to="/discover/identity"
                className="rounded-lg bg-accent px-4 py-2.5 text-sm font-medium tracking-wide text-ink transition-colors hover:bg-accent-soft"
              >
                Start a conversation
              </Link>
            }
          />
        ) : (
          <Field divided>
            {traits.map(([name, signal]) => (
              <div key={name} className="py-4 first:pt-0 last:pb-0">
                <div className="flex items-baseline justify-between">
                  <h3 className="text-sm font-medium text-ink">{traitLabel(name)}</h3>
                  <span className="font-mono text-xs text-accent-soft">{qualitativeLabel(signal.score)}</span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-ink-muted">{signal.summary}</p>
              </div>
            ))}
          </Field>
        )}
      </div>

      {/* Evidence Timeline */}
      <div className="mt-8">
        <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Evidence Timeline</p>
        {evidenceTimeline.length === 0 ? (
          <p className="text-xs text-ink-faint">
            The most recent entries that shaped your Career DNA will appear here once they exist.
          </p>
        ) : (
          <Surface tone="neutral" padding="sm">
            {evidenceTimeline.map((entry) =>
              entry.kind === "observation" ? (
                <ObservationEntry key={entry.id} entry={entry} />
              ) : (
                <BeliefRevisionEntry key={entry.id} entry={entry} />
              ),
            )}
          </Surface>
        )}
      </div>

      {/* How Career DNA is formed */}
      <div className="mt-8">
        <ProcessSteps title="How Career DNA Is Formed" steps={FORMATION_STEPS} />
      </div>
    </div>
  );
}
