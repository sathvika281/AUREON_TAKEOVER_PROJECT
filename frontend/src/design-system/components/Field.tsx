import type { HTMLAttributes } from "react";

import { cn } from "../cn";

/**
 * A borderless group for simple content (steps, evidence entries, a list
 * of readings) — the alternative to reaching for `Surface` by default.
 * `divided` draws a single hairline between direct children instead of a
 * box around all of them; without it, children are simply spaced apart.
 */
interface FieldProps extends HTMLAttributes<HTMLDivElement> {
  divided?: boolean;
}

export function Field({ className, divided, ...props }: FieldProps) {
  return <div className={cn(divided ? "divide-y divide-border" : "space-y-4", className)} {...props} />;
}
