import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Layers, Leaf, Puzzle, ScanEye, ShieldAlert, Sparkles, TreeDeciduous, Sprout as SproutIcon } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { PageHeader } from "../../design-system/components/PageHeader";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { HiddenPotentialResponse, TalentPattern } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";
import { UniverseSummaryCard } from "../discovery/components/UniverseSummaryCard";
import { UniverseWorkspaceTabs } from "../discovery/components/UniverseWorkspaceTabs";
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
    description: "Each pattern names the exact evidence behind it — never a guess dressed up as insight.",
  },
];

const STRONG_EVIDENCE_THRESHOLD = 0.4;

const TIER_SECTIONS: { key: keyof HiddenPotentialResponse["strengths"]; title: string; icon: typeof SproutIcon }[] = [
  { key: "emerging", title: "Emerging", icon: Leaf },
  { key: "growing", title: "Growing", icon: SproutIcon },
  { key: "consistently_observed", title: "Consistently Observed", icon: TreeDeciduous },
];

const SOURCE_LABELS: Record<string, string> = {
  career_dna: "Career DNA",
  experiment: "Experience Lab",
  reflection: "Reflection",
};

function StrengthCard({ pattern }: { pattern: TalentPattern }) {
  return (
    <Surface tone="raised" padding="md">
      <p className="text-sm font-medium text-ink">{traitLabel(pattern.talent)}</p>
      <p className="mt-2 text-sm leading-relaxed text-ink">{pattern.explanation}</p>
      <p className="mt-3 text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Why Aureon believes this</p>
      <ul className="mt-1.5 space-y-1">
        {pattern.evidence.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-ink-muted">
            <Badge tone="neutral" className="shrink-0">{SOURCE_LABELS[item.source] ?? item.source}</Badge>
            <span>{item.description}</span>
          </li>
        ))}
      </ul>
    </Surface>
  );
}

/**
 * Not AI magic — an honest interpretation of real evidence. This is now
 * the single destination for strengths: the existing pairwise trait-
 * combination detection, plus what used to be a separate Talent
 * Discovery Lab page, both rendered from one consolidated backend
 * response (GET .../hidden-potential — see backend
 * domain/services/hidden_potential.py, which composes rather than
 * duplicates the existing engines).
 */
export function HiddenPotentialScreen() {
  const studentId = useRef(getCurrentStudentId()).current;
  const {
    hypotheses, careerDna, confidenceScore, understandingStage, isLoading: isDiscoveryLoading,
  } = useDiscoveryContext();

  const [data, setData] = useState<HiddenPotentialResponse | null>(null);
  // Loading, a genuine fetch failure, and genuinely no strengths yet are
  // three different product states.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  const loadData = useCallback(() => {
    setStatus("loading");
    apiClient
      .get<HiddenPotentialResponse>(`/v1/students/${studentId}/hidden-potential`)
      .then((r) => {
        setData(r);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [studentId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const traits = Object.entries(careerDna);
  const strongTraitCount = data?.discovery_statistics.traits_with_strong_evidence ?? 0;
  const hasAnyStrength = data
    ? data.strengths.emerging.length + data.strengths.growing.length + data.strengths.consistently_observed.length > 0
    : false;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      {!isDiscoveryLoading && (
        <div className="mb-8 space-y-4">
          <UniverseSummaryCard
            hypotheses={hypotheses}
            careerDna={careerDna}
            confidenceScore={confidenceScore}
            understandingStage={understandingStage}
          />
          <UniverseWorkspaceTabs />
        </div>
      )}

      <PageHeader
        title="Hidden Potential"
        description="Everything Aureon has noticed about your strengths — real strengths building over time, and patterns from traits that combine in ways most people don't show. Never a score, always the real evidence behind it."
      />

      {status === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : status === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Hidden Potential"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
            action={<Button variant="secondary" onClick={loadData}>Retry</Button>}
          />
        </div>
      ) : (
        <>
          {/* Discovery Status */}
          <div className="mt-8">
            <Surface tone="neutral" padding="md">
              <div className="flex items-center justify-between">
                <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Discovery Status</p>
                <Badge tone="warm">{understandingStage}</Badge>
              </div>
              <div className="mt-3 flex flex-wrap gap-6">
                <div>
                  <p className="text-lg font-light text-ink">{data?.discovery_statistics.traits_tracked ?? 0}</p>
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">Traits tracked</p>
                </div>
                <div>
                  <p className="text-lg font-light text-ink">{strongTraitCount}</p>
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">With strong evidence</p>
                </div>
                <div>
                  <p className="text-lg font-light text-ink">{data?.discovery_statistics.strengths_found ?? 0}</p>
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">Strengths found</p>
                </div>
                <div>
                  <p className="text-lg font-light text-ink">{data?.discovery_statistics.hidden_patterns_found ?? 0}</p>
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.1em] text-ink-faint">Combined patterns</p>
                </div>
              </div>
            </Surface>
          </div>

          {/* Suggested Experience — exactly one recommendation, reused verbatim from Progressive Discovery */}
          {data?.suggested_experience && (
            <div className="mt-6">
              <Surface tone="raised" padding="md">
                <p className="flex items-center gap-1.5 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
                  <Sparkles size={11} /> Build More Evidence
                </p>
                <p className="mt-2 text-sm leading-relaxed text-ink">
                  Try "{data.suggested_experience.title}" in Experience Lab to keep strengthening what Aureon has noticed.
                </p>
                <Link
                  to="/discover/experience-lab"
                  className="mt-2 inline-block text-xs font-medium text-accent-soft transition-colors hover:text-accent"
                >
                  Go to Experience Lab →
                </Link>
              </Surface>
            </div>
          )}

          {/* Your Strengths */}
          <div className="mt-8">
            <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Your Strengths</p>
            {hasAnyStrength ? (
              <div className="space-y-8">
                {TIER_SECTIONS.map(({ key, title, icon: Icon }) => {
                  const inTier = data?.strengths[key] ?? [];
                  if (inTier.length === 0) return null;
                  return (
                    <div key={key}>
                      <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-ink-muted">
                        <Icon size={13} className="text-accent-soft" /> {title}
                      </p>
                      <div className="space-y-4">
                        {inTier.map((pattern) => (
                          <StrengthCard key={pattern.talent} pattern={pattern} />
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <EmptyStatePanel
                icon={SproutIcon}
                title="Still Discovering"
                description="Aureon hasn't gathered enough real evidence yet — a conversation, a reflection, or an Experience Lab activity can all contribute. Strengths can appear at any point."
              />
            )}
          </div>

          {/* Pattern Detection explainer */}
          <div className="mt-8">
            <ProcessSteps title="How Pattern Detection Works" steps={DETECTION_STEPS} />
          </div>

          {/* Cross-Evidence Analysis — the existing pairwise trait-combination patterns */}
          <div className="mt-8">
            <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Cross-Evidence Analysis</p>
            {data && data.hidden_patterns.length > 0 ? (
              <div className="space-y-4">
                {data.hidden_patterns.map((pattern) => (
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
            ) : (
              <EmptyStatePanel
                icon={Puzzle}
                title="Signals Waiting"
                description={
                  strongTraitCount >= 2
                    ? "Traits with strong evidence exist, but Aureon hasn't found a combination between them worth surfacing yet. Keep exploring — this can appear at any point."
                    : strongTraitCount === 1
                      ? "One trait currently has strong evidence behind it. This needs at least two before it can look for a pattern between them."
                      : "No traits have strong evidence yet. Keep talking with Aureon in Identity Discovery to build up your Career DNA — patterns can only form once individual traits are well supported."
                }
                action={
                  <Link
                    to="/discover/identity"
                    className="rounded-lg bg-accent px-4 py-2.5 text-sm font-medium tracking-wide text-ink transition-colors hover:bg-accent-soft"
                  >
                    Continue Identity Discovery
                  </Link>
                }
              />
            )}
          </div>

          {/* Evidence Timeline — the merged, chronological feed behind every strength */}
          {data && data.evidence_timeline.length > 0 && (
            <div className="mt-8">
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Evidence Timeline</p>
              <div className="space-y-2">
                {data.evidence_timeline.map((item, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-lg border border-border bg-surface px-3 py-2.5">
                    <Badge tone="neutral" className="mt-0.5 shrink-0">{traitLabel(item.talent)}</Badge>
                    <div>
                      <p className="text-xs text-ink-muted">{item.description}</p>
                      <p className="mt-0.5 text-[0.65rem] text-ink-faint">{SOURCE_LABELS[item.source] ?? item.source}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Signals gathered so far, for transparency */}
          {traits.length > 0 && (
            <div className="mt-8">
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Signals Gathered So Far</p>
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
        </>
      )}
    </div>
  );
}
