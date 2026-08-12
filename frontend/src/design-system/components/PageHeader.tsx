import type { ReactNode } from "react";

import { cn } from "../cn";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

/**
 * The eyebrow / h1 / description (+ optional right-side action) pattern
 * hand-copied near-verbatim across most screens — formalized here rather
 * than left as copy-pasted markup. Every prop but `title` is optional;
 * `action` renders as-is (not forced into a row), so a screen with a
 * stacked action group (e.g. a button above a text link) keeps its own
 * internal layout rather than being flattened into one this component
 * assumes.
 */
export function PageHeader({ eyebrow, title, description, action, className }: PageHeaderProps) {
  return (
    <div className={cn("flex items-start justify-between gap-4", className)}>
      <div>
        {eyebrow && (
          <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">{eyebrow}</p>
        )}
        <h1 className={cn("text-2xl font-light text-ink", eyebrow && "mt-2")}>{title}</h1>
        {description && <p className="mt-2 text-sm leading-relaxed text-ink-muted">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
