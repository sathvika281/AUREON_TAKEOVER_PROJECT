interface MarkProps {
  size?: number;
  className?: string;
}

/** Shared call signature with Lucide icons (`size`/`className`), so a
 * `Mark` can stand in anywhere a `LucideIcon` prop is accepted. */
export type MarkComponent = (props: MarkProps) => JSX.Element;

/**
 * Aureon's meaning-carrying icon vocabulary — Orbit, Trajectory, Signal,
 * Discovery, Growth, Journey. Used wherever a component is making a
 * *meaning* statement (ProcessSteps, EmptyStatePanel) rather than
 * offering a functional control (those stay Lucide). Each mark uses
 * `currentColor` so it drops in exactly where a Lucide icon did —
 * `size`/`className` match that same call shape. Same restrained
 * single-accent vocabulary as AureonMark: thin strokes, one filled
 * "seed" point, never more than one color.
 */

export function OrbitMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} fill="none" aria-hidden="true">
      <ellipse cx="12" cy="12" rx="9" ry="4.5" transform="rotate(-20 12 12)" stroke="currentColor" strokeWidth="1.3" opacity="0.85" />
      <circle cx="19.2" cy="9.4" r="1.4" fill="currentColor" />
      <circle cx="12" cy="12" r="1.1" fill="currentColor" opacity="0.55" />
    </svg>
  );
}

export function TrajectoryMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} fill="none" aria-hidden="true">
      <path
        d="M4 18 C 8 18, 10 10, 20 5"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeDasharray="1 3.4"
        strokeLinecap="round"
        opacity="0.85"
      />
      <circle cx="20" cy="5" r="1.3" fill="currentColor" />
      <circle cx="4" cy="18" r="1" fill="currentColor" opacity="0.45" />
    </svg>
  );
}

export function SignalMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="1.6" fill="currentColor" />
      <circle cx="12" cy="12" r="5.5" stroke="currentColor" strokeWidth="1.2" opacity="0.55" />
      <circle cx="12" cy="12" r="9.3" stroke="currentColor" strokeWidth="1.2" opacity="0.28" />
    </svg>
  );
}

export function DiscoveryMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} fill="none" aria-hidden="true">
      <circle
        cx="12" cy="12" r="8"
        stroke="currentColor" strokeWidth="1.3"
        strokeDasharray="42 8" strokeLinecap="round"
        transform="rotate(-90 12 12)"
        opacity="0.85"
      />
      <circle cx="12" cy="12" r="2" fill="currentColor" opacity="0.7" />
    </svg>
  );
}

export function GrowthMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path d="M12 20 L12 11" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" fill="none" opacity="0.8" />
      <path d="M12 13 C 9.5 13, 8 10.5, 9 8 C 11.5 8.5, 12.5 11, 12 13 Z" fill="currentColor" opacity="0.9" />
      <path d="M12 13 C 14.5 13, 16 10.5, 15 8 C 12.5 8.5, 11.5 11, 12 13 Z" fill="currentColor" opacity="0.65" />
      <circle cx="12" cy="20.5" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function JourneyMark({ size = 24, className = "" }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden="true">
      <circle cx="4" cy="18" r="0.8" fill="currentColor" opacity="0.35" />
      <circle cx="8.5" cy="15.5" r="1.1" fill="currentColor" opacity="0.55" />
      <circle cx="13.5" cy="12.5" r="1.4" fill="currentColor" opacity="0.75" />
      <circle cx="19" cy="9" r="1.8" fill="currentColor" />
    </svg>
  );
}
