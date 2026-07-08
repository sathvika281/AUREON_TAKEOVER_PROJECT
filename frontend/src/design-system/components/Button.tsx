import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../cn";

const buttonStyles = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-colors duration-300 disabled:cursor-not-allowed disabled:opacity-40",
  {
    variants: {
      variant: {
        primary: "bg-accent text-ink hover:bg-accent-soft",
        ghost: "bg-transparent text-ink-muted hover:bg-white/5 hover:text-ink",
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
