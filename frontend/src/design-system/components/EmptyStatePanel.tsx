import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Surface } from "./Surface";
import type { MarkComponent } from "./Marks";

/**
 * The "waiting for evidence" panel — reused wherever a screen has nothing
 * to show yet. Always states what's missing and how it gets filled in,
 * never a bare "Nothing yet." The glyph sits inside an open, gapped ring
 * (echoing `Marks`' aperture vocabulary) rather than a solid bordered
 * circle — something waiting to be completed, not a filled container.
 */
export function EmptyStatePanel({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon | MarkComponent;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Surface tone="neutral" padding="lg" className="text-center">
      <div className="relative mx-auto flex h-12 w-12 items-center justify-center text-ink-faint">
        <svg viewBox="0 0 48 48" className="absolute inset-0 h-full w-full" aria-hidden="true">
          <circle
            cx="24" cy="24" r="21" fill="none" stroke="currentColor" strokeWidth="1"
            strokeDasharray="110 22" strokeLinecap="round" opacity="0.35"
          />
        </svg>
        <Icon size={17} />
      </div>
      <h3 className="mt-5 text-sm font-medium text-ink">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-xs leading-relaxed text-ink-muted">{description}</p>
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </Surface>
  );
}
