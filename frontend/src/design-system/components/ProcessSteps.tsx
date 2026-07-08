import type { LucideIcon } from "lucide-react";

import { Surface } from "./Surface";

export interface ProcessStep {
  icon: LucideIcon;
  title: string;
  description: string;
}

/**
 * A numbered "how this works" explainer — reused across every screen that
 * needs to teach its mechanism before evidence exists (Career DNA, Hidden
 * Potential, Decision Lab, Parallel Universe, Mentor Match, and the locked
 * Build-stage modules). Purely educational copy, never real data.
 */
export function ProcessSteps({ title, steps }: { title?: string; steps: ProcessStep[] }) {
  return (
    <Surface tone="neutral" padding="md">
      {title && <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{title}</p>}
      <div className={title ? "mt-4 space-y-4" : "space-y-4"}>
        {steps.map((step, i) => {
          const Icon = step.icon;
          return (
            <div key={i} className="flex gap-3">
              <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-border bg-surface-raised text-ink-faint">
                <Icon size={14} />
              </div>
              <div>
                <p className="text-sm font-medium text-ink">{step.title}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-ink-muted">{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </Surface>
  );
}
