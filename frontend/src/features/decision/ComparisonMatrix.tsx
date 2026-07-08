import { Surface } from "../../design-system/components/Surface";
import type { CareerComparison } from "../../shared/api/types";

const DIMENSION_LABELS: Record<string, string> = {
  work_style: "Work style",
  creativity: "Creativity",
  research: "Research",
  collaboration: "Collaboration",
  work_life_balance: "Work-life balance",
  growth: "Growth",
  future_demand: "Future demand",
  required_education: "Required education",
  skills: "Skills",
  lifestyle: "Lifestyle",
  salary: "Salary",
  travel: "Travel",
  stress: "Stress",
  flexibility: "Flexibility",
  entrepreneurship_potential: "Entrepreneurship potential",
};

/**
 * Every fact shown here is read directly from the Career Knowledge Base
 * (deterministic, not LLM-invented) — only the "why it matters to you"
 * line is personalized reasoning.
 */
export function ComparisonMatrix({ comparison }: { comparison: CareerComparison }) {
  const careerIds = comparison.career_ids;

  return (
    <div className="space-y-4">
      <Surface tone="neutral" padding="md">
        <p className="text-sm leading-relaxed text-ink">{comparison.summary_reason}</p>
        {comparison.missing_evidence.length > 0 && (
          <div className="mt-3 border-t border-border pt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Missing evidence</p>
            <ul className="mt-1.5 space-y-0.5">
              {comparison.missing_evidence.map((item, i) => (
                <li key={i} className="text-xs text-ink-faint">
                  <span>–</span> {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Surface>

      {comparison.dimensions.map((dim) => (
        <Surface key={dim.dimension} tone="raised" padding="md">
          <p className="text-xs uppercase tracking-widest text-accent-soft">
            {DIMENSION_LABELS[dim.dimension] ?? dim.dimension}
          </p>
          <div className="mt-2 grid gap-3" style={{ gridTemplateColumns: `repeat(${careerIds.length}, minmax(0, 1fr))` }}>
            {careerIds.map((id) => (
              <div key={id}>
                <p className="text-[0.68rem] text-ink-faint">{comparison.career_names[id] ?? id}</p>
                <p className="mt-1 text-xs leading-relaxed text-ink-muted">{dim.per_career[id] ?? "Not available"}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 rounded-lg bg-white/[0.03] px-3 py-2 text-xs italic leading-relaxed text-ink-muted">
            {dim.why_it_matters_to_you}
          </p>
        </Surface>
      ))}
    </div>
  );
}
