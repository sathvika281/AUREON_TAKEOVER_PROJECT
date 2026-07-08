import { Surface } from "../../design-system/components/Surface";
import type { CareerReality } from "../../shared/api/types";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{label}</p>
      <p className="mt-1 text-sm leading-relaxed text-ink-muted">{value}</p>
    </div>
  );
}

/**
 * Educational, not promotional — every field here is an honest structured
 * answer to "what is this career actually like?", not marketing copy.
 */
export function RealitySection({ reality }: { reality: CareerReality }) {
  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      <Field label="Daily work" value={reality.daily_work} />
      <Field label="Work environment" value={reality.work_environment} />
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Collaboration level" value={reality.collaboration_level} />
        <Field label="Creativity level" value={reality.creativity_level} />
        <Field label="Research intensity" value={reality.research_intensity} />
        <Field label="Learning curve" value={reality.learning_curve} />
        <Field label="Travel" value={reality.travel} />
        <Field label="Remote possibility" value={reality.remote_possibility} />
      </div>
      <Field label="Stress factors" value={reality.stress_factors} />
      <Field label="Typical challenges" value={reality.typical_challenges} />
      <Field label="Common misconceptions" value={reality.misconceptions} />
      <Field label="Long-term growth" value={reality.long_term_growth} />
      <Field label="Required education" value={reality.required_education} />

      {reality.required_skills.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Required skills</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {reality.required_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-white/5 px-2.5 py-1 text-xs text-ink-muted"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {reality.salary_ranges.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Salary ranges</p>
          <ul className="mt-1.5 space-y-1">
            {reality.salary_ranges.map((s, i) => (
              <li key={i} className="text-xs text-ink-muted">
                <span className="text-ink">{s.region}:</span> {s.range}
                {s.note && <span className="text-ink-faint"> — {s.note}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Surface>
  );
}
