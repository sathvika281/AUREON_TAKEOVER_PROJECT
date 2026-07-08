import type { InputHTMLAttributes } from "react";

import { cn } from "../cn";

/** Formalizes the raw `<input>` Tailwind classes already established
 * ad-hoc in GitHubIntelligenceScreen.tsx/SearchInvestigationScreen.tsx —
 * one shared component instead of the same class string repeated. */
export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-xl border border-border bg-surface px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/40 focus:outline-none",
        className,
      )}
      {...props}
    />
  );
}
