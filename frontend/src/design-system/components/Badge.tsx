import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "../cn";

const badgeStyles = cva(
  "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[0.65rem] font-medium uppercase tracking-[0.09em]",
  {
    variants: {
      tone: {
        neutral: "border-border text-ink-faint",
        // "warm" — the prominent tier (e.g. high confidence, shortlisted):
        // the one place a badge may use the accent color.
        warm: "border-accent/30 bg-accent/10 text-accent-soft",
        // "cool" — a middle tier, distinguished by weight rather than a
        // second hue, since the palette has only one accent.
        cool: "border-border-strong text-ink-muted",
        // "gold" — a genuine achievement/milestone moment only, never a
        // general-purpose second accent.
        gold: "border-gold/30 bg-gold/10 text-gold-soft",
        // "success" — real system status only (ready, complete, online,
        // healthy), never a general-purpose accent.
        success: "border-success/30 bg-success/10 text-success-soft",
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
