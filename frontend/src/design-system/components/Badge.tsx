import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "../cn";

const badgeStyles = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.7rem] font-medium uppercase tracking-wide",
  {
    variants: {
      tone: {
        neutral: "bg-white/5 text-ink-muted",
        // "warm" — the prominent tier (e.g. high confidence, shortlisted):
        // the one place a badge may use the accent color.
        warm: "bg-accent/15 text-accent-soft",
        // "cool" — a middle tier, distinguished by a border rather than a
        // second hue, since the palette has only one accent.
        cool: "border border-border text-ink-muted",
      },
    },
    defaultVariants: {
      tone: "neutral",
    },
  },
);

interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeStyles> {}

export function Badge({ className, tone, ...props }: BadgeProps) {
  return <span className={cn(badgeStyles({ tone }), className)} {...props} />;
}
