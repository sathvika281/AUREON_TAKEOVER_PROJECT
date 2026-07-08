import { Link } from "react-router-dom";
import { Layers, Puzzle, ScanEye, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { traitLabel } from "../discovery/network/layoutTraits";

const DETECTION_STEPS = [
  {
    icon: ScanEye,
    title: "Aureon watches every trait, not just one at a time",
    description: "As Career DNA traits accumulate evidence, Aureon keeps track of which ones are becoming well-supported.",
  },
  {
    icon: Layers,
    title: "It looks for meaningful combinations",
    description: "When two well-evidenced traits sit together in a way most people wouldn't naturally connect, that's a candidate pattern.",
  },
  {
    icon: Puzzle,
    title: "A pattern only surfaces with real support",
    description: "Each Hidden Potential pattern names the exact two traits behind it and the evidence for both — never a guess dressed up as insight.",
  },
];

const STRONG_EVIDENCE_THRESHOLD = 0.4;

/**
 * Not AI magic — an honest interpretation of real evidence. Every
 * pattern states the two real trait readings behind it. Computed
 * server-side now (see backend agents/specialized/discovery/
 * hidden_potential.py) so it's consistent everywhere and survives a new
 * device like everything else in the Notebook.
 */
export function HiddenPotentialScreen() {
  const { hiddenPotential, careerDna, understandingStage } = useDiscoveryContext();

  const traits = Object.entries(careerDna);
  const strongTraits = traits.filter(([, signal]) => (signal.score ?? 0) >= STRONG_EVIDENCE_THRESHOLD);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Hidden Potential</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Patterns Aureon noticed by comparing traits that are both well-supported by evidence —
        not a claim to know more than the data shows.
      </p>

      {/* Discovery Status */}
      <div className="mt-8">
        <Surface tone="neutral" padding="md">
          <div className="flex items-center justify-between">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Discovery Status</p>
            <Badge tone="warm">{understandingStage}</Badge>
          </div>
          <div className="mt-3 flex gap-6">
            <div>
              <p className="text-lg font-light text-ink">{traits.length}</p>
              <p className="text-[0.68rem] text-ink-faint">Traits tracked</p>
            </div>
            <div>
              <p className="text-lg font-light text-ink">{strongTraits.length}</p>
              <p className="text-[0.68rem] text-ink-faint">With strong evidence</p>
            </div>
            <div>
              <p className="text-lg font-light text-ink">{hiddenPotential.length}</p>
              <p className="text-[0.68rem] text-ink-faint">Patterns found</p>
            </div>
          </div>
        </Surface>
      </div>

      {/* Pattern Detection */}
      <div className="mt-6">
        <ProcessSteps title="How Pattern Detection Works" steps={DETECTION_STEPS} />
      </div>

      {/* Cross-Evidence Analysis */}
      <div className="mt-8">
        <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Cross-Evidence Analysis</p>
        {hiddenPotential.length > 0 ? (
          <div className="space-y-4">
            {hiddenPotential.map((pattern) => (
              <Surface key={pattern.id} tone="raised" padding="md">
                <p className="text-sm leading-relaxed text-ink">{pattern.sentence}</p>
                <p className="mt-2 text-xs text-ink-faint">
                  Based on strong evidence for both {pattern.trait_a} and {pattern.trait_b}.
                </p>
                {pattern.supporting_evidence.length > 0 && (
                  <ul className="mt-2 space-y-0.5">
                    {pattern.supporting_evidence.map((item, i) => (
                      <li key={i} className="text-xs text-ink-muted">
                        <span className="text-accent">＋</span> {item}
                      </li>
                    ))}
                  </ul>
                )}
              </Surface>
            ))}
          </div>
        ) : strongTraits.length >= 2 ? (
          <EmptyStatePanel
            icon={Sparkles}
            title="Still looking for a meaningful combination"
            description={`You have ${strongTraits.length} traits with strong evidence, but Aureon hasn't found a combination between them worth surfacing yet. Keep exploring — this can appear at any point.`}
          />
        ) : (
          <EmptyStatePanel
            icon={Puzzle}
            title="Signals Waiting"
            description={
              strongTraits.length === 1
                ? "One trait currently has strong evidence behind it. Hidden Potential needs at least two before it can look for a pattern between them."
                : "No traits have strong evidence yet. Keep talking with Aureon in Identity Discovery to build up your Career DNA — patterns can only form once individual traits are well supported."
            }
            action={
              <Link
                to="/discover/identity"
                className="rounded-xl bg-accent px-4 py-2.5 text-sm font-medium text-ink transition hover:bg-accent-soft"
              >
                Continue Identity Discovery
              </Link>
            }
          />
        )}
      </div>

      {/* Signals gathered so far, for transparency */}
      {traits.length > 0 && (
        <div className="mt-8">
          <p className="mb-3 px-1 text-xs uppercase tracking-widest text-ink-faint">Signals Gathered So Far</p>
          <div className="flex flex-wrap gap-2">
            {traits.map(([name, signal]) => (
              <span
                key={name}
                className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-ink-muted"
              >
                {traitLabel(name)}
                {(signal.score ?? 0) >= STRONG_EVIDENCE_THRESHOLD && (
                  <span className="ml-1.5 text-accent-soft">●</span>
                )}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
