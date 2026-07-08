import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "../cn";

const surfaceStyles = cva("rounded-xl border", {
  variants: {
    tone: {
      neutral: "border-border bg-surface",
      raised: "border-border bg-surface-raised",
    },
    padding: {
      none: "",
      sm: "p-3",
      md: "p-5",
      lg: "p-7",
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
