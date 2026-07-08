import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Rocket, ShieldCheck, TrendingUp, Wrench } from "lucide-react";

import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { CareerDetail } from "../../shared/api/types";
import { useCareerExplorationContext } from "../career-exploration/CareerExplorationContext";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { TimelineComparison } from "./TimelineComparison";

const ANALYSIS_STEPS = [
  {
    icon: TrendingUp,
    title: "Demand trajectory",
    description: "How a career's demand is expected to shift by 2030, 2035, and 2040 — grounded in the career's real profile, not a guess about the future.",
  },
  {
    icon: Wrench,
    title: "Automation impact, today",
    description: "An honest read of what's already being automated in this line of work, and what still requires a person.",
  },
  {
    icon: ShieldCheck,
    title: "What stays valuable",
    description: "The specific skills that remain valuable as the work changes — never framed as 'AI will replace this,' always what to build toward.",
  },
];

const TIMELINE_STAGES = ["Today", "2030", "2035", "2040"];

function FutureLensPlaceholder() {
  return (
    <Surface tone="raised" padding="md">
      <p className="text-sm font-medium text-ink">Timeline Structure</p>
      <p className="mt-2 text-xs leading-relaxed text-ink-muted">
        Once a career is selected, this space fills in with its real outlook across each stage below.
      </p>
      <div className="mt-4 grid grid-cols-4 gap-2 border-t border-border pt-4">
        {TIMELINE_STAGES.map((stage) => (
          <div key={stage}>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{stage}</p>
            <p className="mt-1 text-xs text-ink-faint">—</p>
          </div>
        ))}
      </div>
    </Surface>
  );
}

/**
 * An aggregate view — Today -> 2030 -> 2035 -> 2040 compared across the
 * student's current candidate careers, or a single career if arrived at
 * via a Career Details page's "See this career's Future Lens" link.
 */
export function FutureLensScreen() {
  const [searchParams] = useSearchParams();
  const singleCareerId = searchParams.get("career");
  const { candidates } = useCareerIntelligenceContext();
  const { recordEvent } = useCareerExplorationContext();

  const [careers, setCareers] = useState<CareerDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const ids = singleCareerId ? [singleCareerId] : candidates.map((c) => c.career_id);
    if (ids.length === 0) {
      setCareers([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    Promise.all(ids.map((id) => apiClient.get<CareerDetail>(`/v1/careers/${id}`)))
      .then((results) => {
        setCareers(results);
        for (const career of results) {
          void recordEvent(career.id, "future_lens_explored", { career_name: career.name });
        }
      })
      .catch(() => setCareers([]))
      .finally(() => setIsLoading(false));
    // recordEvent identity is stable for the provider's lifetime; only
    // re-fetch/re-log when the actual set of careers to show changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [singleCareerId, candidates]);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Future Lens</h1>
      <p className="mt-2 text-sm text-ink-muted">
        How careers are expected to evolve — never "AI will replace this," always a grounded look
        at demand, automation, and what stays valuable over time.
      </p>

      <div className="mt-8">
        <ProcessSteps title="What Future Lens Analyzes" steps={ANALYSIS_STEPS} />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <p className="text-sm text-ink-faint">Loading…</p>
        ) : careers.length === 0 ? (
          <div className="space-y-4">
            <FutureLensPlaceholder />
            <p className="flex items-center gap-2 text-xs text-ink-faint">
              <Rocket size={13} />
              Analyze your fit in Career Intelligence first, or open a career from Career Reality, to
              see its future outlook here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {careers.map((career) => (
              <TimelineComparison key={career.id} careerName={career.name} futureLens={career.future_lens} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
