import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "../cn";

// A crafted instrument, not a card in a stack of identical cards — a
// hairline edge, a barely-raised plane, never a heavy drop shadow.
const surfaceStyles = cva("rounded-2xl border backdrop-blur-[2px] transition-colors duration-300", {
  variants: {
    tone: {
      neutral: "border-border bg-surface/90",
      raised: "border-border-strong bg-surface-raised/92",
    },
    padding: {
      none: "",
      sm: "p-4",
      md: "p-6",
      lg: "p-8",
    },
  },
  defaultVariants: {
    tone: "neutral",
    padding: "md",
  },
});

interface SurfaceProps extends HTMLAttributes<HTMLDivElement>, VariantProps<typeof surfaceStyles> {}

export function Surface({ className, tone, padding, ...props }: SurfaceProps) {
  return <div className={cn(surfaceStyles({ tone, padding }), className)} {...props} />;
}
