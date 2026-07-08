import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Surface } from "./Surface";

/**
 * The "waiting for evidence" panel — reused wherever a screen has nothing
 * to show yet. Always states what's missing and how it gets filled in,
 * never a bare "Nothing yet."
 */
export function EmptyStatePanel({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Surface tone="neutral" padding="lg" className="text-center">
      <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-full border border-border bg-surface-raised text-ink-faint">
        <Icon size={18} />
      </div>
      <h3 className="mt-4 text-sm font-medium text-ink">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-xs leading-relaxed text-ink-muted">{description}</p>
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </Surface>
  );
}
