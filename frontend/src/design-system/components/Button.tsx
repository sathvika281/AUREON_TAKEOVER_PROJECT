import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../cn";

const buttonStyles = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-medium tracking-wide transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-40",
  {
    variants: {
      variant: {
        primary: "bg-accent text-ink hover:bg-accent-soft",
        // A hairline appears on interaction rather than a filled hover
        // state — an instrument responding, not a generic UI-kit button.
        ghost: "border border-transparent bg-transparent text-ink-muted hover:border-border hover:text-ink",
        // A visible hairline at rest, not just on hover — for a real,
        // standalone secondary action (Retry, "Try This") that needs its
        // own outline rather than blending into plain text until touched.
        // Formalizes the border-border/text-ink-muted className already
        // hand-copied across several screens.
        secondary: "border border-border text-ink-muted hover:border-border-strong hover:text-ink",
      },
      size: {
        md: "px-4 py-2.5",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonStyles> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonStyles({ variant, size }), className)} {...props} />;
}
