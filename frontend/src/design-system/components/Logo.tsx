interface AureonMarkProps {
  size?: number;
  className?: string;
  /** Drops the compass ticks, outward arrows, and evidence nodes for
   * legibility at small sizes — auto-decided from `size` unless set. */
  simplified?: boolean;
}

/**
 * The Aureon mark. Seven symbolic layers, read outside-in:
 * an open outer ring (career discovery is never truly complete), four
 * reduced compass ticks with open-ended arrows (guidance, not
 * prescription — multiple paths, none forced), scattered evidence nodes
 * (every conversation, document, repo, URL and reflection Aureon has
 * gathered), a single curved path breaking out and upward (understanding
 * before direction), two asymmetric leaves, and the seed they both grow
 * from (every student's hidden potential). One accent color throughout,
 * at varying opacity — never a second hue.
 */
export function AureonMark({ size = 24, className = "", simplified }: AureonMarkProps) {
  const isSimple = simplified ?? size <= 28;

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className={className} aria-hidden="true">
      {!isSimple && (
        <circle
          cx="50" cy="50" r="44" fill="none" className="stroke-accent/25"
          strokeWidth="2" strokeDasharray="248 14" strokeLinecap="round"
          transform="rotate(-98 50 50)"
        />
      )}
      {!isSimple && (
        <g className="stroke-accent" strokeWidth="2" strokeLinecap="round" fill="none" opacity="0.6">
          <path d="M50 26 L50 17 M46.5 20.5 L50 16 L53.5 20.5" />
          <path d="M74 50 L83 50 M79.5 46.5 L84 50 L79.5 53.5" />
          <path d="M65.5 65.5 L72 72 M65 66.7 L72.3 72 L71 64.7" />
          <path d="M34.5 65.5 L28 72 M35 66.7 L27.7 72 L29 64.7" transform="scale(-1,1) translate(-100,0)" />
        </g>
      )}
      {!isSimple && (
        <g className="fill-accent-soft">
          <circle cx="50" cy="17" r="2" />
          <circle cx="83" cy="50" r="2" />
          <circle cx="72" cy="72" r="2" />
          <circle cx="28" cy="72" r="2" />
        </g>
      )}
      <path
        d="M50 58 C 38 62, 30 54, 30 42 C 30 32, 38 25, 48 24"
        fill="none" className="stroke-accent-soft" strokeWidth="2.4" strokeLinecap="round"
      />
      <path
        d="M50 50 C 44 44, 44 34, 50 28 C 56 34, 56 44, 50 50 Z"
        className="fill-accent" transform="rotate(-18 50 50)"
      />
      <path
        d="M50 50 C 44 44, 44 34, 50 28 C 56 34, 56 44, 50 50 Z"
        className="fill-accent" transform="rotate(18 50 50) scale(0.86) translate(8,8)"
      />
      <ellipse cx="50" cy="53" rx="8.5" ry="10.5" className="fill-ink" />
    </svg>
  );
}

const LOGO_SIZES = {
  sm: { mark: 20, word: "text-sm", tagline: "text-[8.5px]", gap: "gap-2" },
  md: { mark: 28, word: "text-base", tagline: "text-[9.5px]", gap: "gap-2.5" },
  lg: { mark: 44, word: "text-xl", tagline: "text-[10.5px]", gap: "gap-3" },
} as const;

interface LogoProps {
  size?: keyof typeof LOGO_SIZES;
  withTagline?: boolean;
  className?: string;
}

/** The full wordmark lockup — mark plus "Aureon," with a single
 * accent-colored letter as the only spot of color in the type itself. */
export function Logo({ size = "md", withTagline = false, className = "" }: LogoProps) {
  const cfg = LOGO_SIZES[size];
  return (
    <div className={`flex items-center ${cfg.gap} ${className}`}>
      <AureonMark size={cfg.mark} />
      <div>
        <div className={`${cfg.word} font-semibold tracking-wide text-ink`}>
          Aur<span className="text-accent-soft">e</span>on
        </div>
        {withTagline && (
          <div className={`${cfg.tagline} font-medium uppercase tracking-[0.16em] text-ink-faint`}>
            Evidence Before Direction
          </div>
        )}
      </div>
    </div>
  );
}
