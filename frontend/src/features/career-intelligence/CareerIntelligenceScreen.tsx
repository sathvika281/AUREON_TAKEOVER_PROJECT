import { Link } from "react-router-dom";
import { FileSearch, Radar, ScanSearch, Sprout } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { CandidateCard } from "./CandidateCard";
import { useCareerIntelligenceContext } from "./CareerIntelligenceContext";

const HOW_IT_WORKS_STEPS = [
  {
    icon: Radar,
    title: "Reads your real Career DNA",
    description: "Every trait Aureon has evidenced about you — nothing from a generic quiz or personality archetype.",
  },
  {
    icon: ScanSearch,
    title: "Compares it against the Career Knowledge Base",
    description: "Careers are reasoned against your evidence one at a time, not ranked against each other by popularity.",
  },
  {
    icon: FileSearch,
    title: "Shows its work either way",
    description: "Every candidate lists the supporting evidence behind it and the evidence that's still missing — a fit is never asserted without both.",
  },
];

export function CareerIntelligenceScreen() {
  const {
    candidates,
    insufficientEvidence,
    insufficientEvidenceReason,
    isAnalyzing,
    error,
    hasAnalyzedOnce,
    recommendedColleges,
    recommendedExperts,
    analyzeCareers,
    shortlistCandidate,
    removeCandidate,
  } = useCareerIntelligenceContext();
  const { careerDna, notebookEntries } = useDiscoveryContext();

  const traitCount = Object.keys(careerDna).length;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Career Intelligence</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Where could someone like you thrive? Every career here is reasoned from your real Career
        DNA and evidence — never a recommendation, always something to keep exploring.
      </p>

      {/* Investigation status */}
      <div className="mt-6">
        <Surface tone="neutral" padding="md">
          <div className="flex items-center justify-between">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Investigation Status</p>
            <Badge tone={hasAnalyzedOnce ? "warm" : "neutral"}>
              {hasAnalyzedOnce ? "Analyzed" : "Not Yet Analyzed"}
            </Badge>
          </div>
          <div className="mt-3 flex gap-6">
            <div>
              <p className="text-lg font-light text-ink">{traitCount}</p>
              <p className="text-[0.68rem] text-ink-faint">Traits evidenced</p>
            </div>
            <div>
              <p className="text-lg font-light text-ink">{notebookEntries.length}</p>
              <p className="text-[0.68rem] text-ink-faint">Notebook entries</p>
            </div>
            <div>
              <p className="text-lg font-light text-ink">{candidates.length}</p>
              <p className="text-[0.68rem] text-ink-faint">Career candidates</p>
            </div>
          </div>
        </Surface>
      </div>

      <div className="mt-6">
        <Button onClick={analyzeCareers} disabled={isAnalyzing}>
          {isAnalyzing ? "Analyzing…" : hasAnalyzedOnce ? "Re-analyze My Fit" : "Analyze My Fit"}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {insufficientEvidence && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={Sprout}
            title="Not Enough Evidence Yet"
            description={
              insufficientEvidenceReason ??
              "Aureon needs more evidence in your Career DNA before it can reason about career fit responsibly."
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
        </div>
      )}

      {!insufficientEvidence && candidates.length === 0 && !isAnalyzing && (
        <div className="mt-6">
          <EmptyStatePanel
            icon={ScanSearch}
            title="No Investigation Run Yet"
            description="Analyze your fit above to see career candidates reasoned from your current Career DNA. This can be re-run any time — it always reflects your latest evidence."
          />
        </div>
      )}

      {candidates.length > 0 && (
        <div className="mt-8 space-y-4">
          {candidates.map((candidate) => (
            <CandidateCard
              key={candidate.career_id}
              candidate={candidate}
              onShortlist={shortlistCandidate}
              onRemove={removeCandidate}
            />
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

      <div className="mt-8">
        <ProcessSteps title="How Career Intelligence Works" steps={HOW_IT_WORKS_STEPS} />
      </div>
    </div>
  );
}
