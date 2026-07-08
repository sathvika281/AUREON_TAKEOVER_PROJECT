import { Link } from "react-router-dom";
import { Compass, Layers, MessagesSquare, ScanSearch, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
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
  const { careerDna, notebookEntries, confidenceScore, understandingStage } = useDiscoveryContext();
  const traits = Object.entries(careerDna);

  const evidenceTimeline = [...notebookEntries]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Career DNA</h1>
      <p className="mt-2 text-sm text-ink-muted">
        A living profile, built from evidence rather than a one-time quiz result.
      </p>

      {/* Current Evidence Summary */}
      <div className="mt-8 grid grid-cols-2 gap-4">
        <Surface tone="neutral" padding="md">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Traits Tracked</p>
          <p className="mt-1.5 text-2xl font-light text-ink">{traits.length}</p>
        </Surface>
        <Surface tone="neutral" padding="md">
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Evidence Entries</p>
          <p className="mt-1.5 text-2xl font-light text-ink">{notebookEntries.length}</p>
        </Surface>
      </div>

      {/* Confidence Progress */}
      <div className="mt-4">
        <Surface tone="neutral" padding="md">
          <div className="flex items-center justify-between">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Confidence Progress</p>
            <Badge tone="warm">{understandingStage}</Badge>
          </div>
          <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out"
              style={{ width: `${Math.round(confidenceScore * 100)}%` }}
            />
          </div>
        </Surface>
      </div>

      {/* Traits Being Built */}
      <div className="mt-8">
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Traits Being Built</p>
        {traits.length === 0 ? (
          <EmptyStatePanel
            icon={Compass}
            title="Waiting for your first signals"
            description="Nothing has been evidenced yet. Traits appear here the moment a conversation gives Aureon something specific to work with."
            action={
              <Link
                to="/discover/identity"
                className="rounded-xl bg-accent px-4 py-2.5 text-sm font-medium text-ink transition hover:bg-accent-soft"
              >
                Start a conversation
              </Link>
            }
          />
        ) : (
          <div className="space-y-4">
            {traits.map(([name, signal]) => (
              <Surface key={name} tone="neutral" padding="md">
                <div className="flex items-baseline justify-between">
                  <h3 className="text-sm font-medium text-ink">{traitLabel(name)}</h3>
                  <span className="text-xs text-accent-soft">{qualitativeLabel(signal.score)}</span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-ink-muted">{signal.summary}</p>
              </Surface>
            ))}
          </div>
        )}
      </div>

      {/* Evidence Timeline */}
      <div className="mt-8">
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Evidence Timeline</p>
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
