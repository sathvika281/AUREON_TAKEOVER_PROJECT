import type { ButtonHTMLAttributes } from "react";

import { cn } from "../cn";

interface FilterPillProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  active: boolean;
}

/**
 * The "All" + category/kind/difficulty filter chip pattern — hand-copied
 * identically across the Skills, Companies, Projects, and Global Trends
 * browse pages — formalized here rather than left as copy-pasted markup.
 */
export function FilterPill({ active, className, ...props }: FilterPillProps) {
  return (
    <button
      type="button"
      className={cn(
        "rounded-full border px-3 py-1 text-xs transition-colors",
        active
          ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
          : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
        className,
      )}
      {...props}
    />
  );
}
