import type { LucideIcon } from "lucide-react";

import { Field } from "./Field";
import type { MarkComponent } from "./Marks";

export interface ProcessStep {
  icon: LucideIcon | MarkComponent;
  title: string;
  description: string;
}

/**
 * A numbered "how this works" explainer — reused across every screen that
 * needs to teach its mechanism before evidence exists (Career DNA, Hidden
 * Potential, Decision Lab, Parallel Universe, Mentor Match, and the locked
 * Build-stage modules). Purely educational copy, never real data. A
 * hairline-divided list, not a boxed card — it appears on nearly every
 * screen in the product, so it shouldn't read as "another container."
 */
export function ProcessSteps({ title, steps }: { title?: string; steps: ProcessStep[] }) {
  return (
    <div>
      {title && (
        <p className="font-mono text-[0.65rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      )}
      <Field divided className={title ? "mt-4" : undefined}>
        {steps.map((step, i) => {
          const Icon = step.icon;
          return (
            <div key={i} className="flex gap-4 py-4 first:pt-0 last:pb-0">
              <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center text-accent-soft/80">
                <Icon size={16} />
              </div>
              <div>
                <p className="text-sm font-medium text-ink">{step.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-ink-muted">{step.description}</p>
              </div>
            </div>
          );
        })}
      </Field>
    </div>
  );
}
