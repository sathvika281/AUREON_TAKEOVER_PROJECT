import { motion } from "framer-motion";
import { useState } from "react";

import { DURATION, EASE_CALM } from "../../../design-system/motion";
import type { EvidenceRecord } from "../../../shared/api/types";
import { explainStar } from "./explainUniverse";
import type { UniverseStar } from "./layoutUniverse";

const STATUS_LABEL: Record<string, string> = {
  investigating: "Investigating",
  growing: "Growing",
  strong: "Strong Signal",
  validated: "Validated",
  discarded: "Rejected",
};

const STATE_FILL: Record<UniverseStar["state"], string> = {
  unexplored: "fill-[#8B87A6]",
  active: "fill-[#D9B87A]",
  rejected: "fill-[#4A4568]",
};

/**
 * One career hypothesis, never anonymous. Position/size/opacity are
 * driven entirely by layoutUniverse's real-data mapping; hover reveals
 * exactly what a judge needs to trust this is reasoning, not decoration —
 * the career name plus its real confidence and status, nothing invented.
 */
export function Star({
  star,
  isSelected,
  boosted = false,
  isHighlighted = false,
  constellationLabel = null,
  evidenceGraph,
  onSelect,
}: {
  star: UniverseStar;
  isSelected: boolean;
  /** True only during a real Wow Moment — a rare, externally-gated
   * brightening, never a self-triggered idle pulse. */
  boosted?: boolean;
  /** True while this star is an endpoint of a currently-hovered
   * constellation line — reuses the same ring visual as isSelected, just a
   * different trigger, so hovering a line also calls out its stars. */
  isHighlighted?: boolean;
  /** Real industry-constellation membership (only set once that
   * constellation's lines are actually shown), surfaced in the hover
   * tooltip so a student doesn't need pixel-precise line targeting to
   * learn a star is part of a group. */
  constellationLabel?: string | null;
  evidenceGraph: EvidenceRecord[];
  onSelect: (star: UniverseStar) => void;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const showTooltip = isHovered && !isSelected;
  const explanation = showTooltip ? explainStar(star, evidenceGraph) : null;
  // Evidence-backed stars are always in the rendered set from the first
  // render — they only ever reposition, never "pop in." A genuinely
  // unexplored star only exists in the DOM once it enters the visible
  // slice (selectVisibleStars), so its very first mount IS the real "a
  // new star appears" event — a real, one-time entrance, not decoration.
  const isFreshReveal = star.state === "unexplored";

  return (
    <motion.g
      initial={isFreshReveal ? { opacity: 0, x: star.x, y: star.y } : false}
      animate={{ x: star.x, y: star.y, opacity: 1 }}
      transition={{ duration: isFreshReveal ? DURATION.reveal : DURATION.drift, ease: EASE_CALM }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect(star)}
      style={{ cursor: "pointer" }}
    >
      <circle r={Math.max(star.size, 10)} fill="transparent" />
      <motion.circle
        initial={false}
        className={STATE_FILL[star.state]}
        animate={{
          opacity: boosted ? Math.min(1, star.opacity + 0.35) : star.opacity,
          r: isSelected ? star.size / 2 + 1.5 : star.size / 2,
        }}
        transition={{ duration: 0.6, ease: EASE_CALM }}
      />
      {boosted && (
        <motion.circle
          r={star.size / 2 + 6}
          fill="#D9B87A"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.25 }}
          transition={{ duration: 1.4, ease: EASE_CALM }}
        />
      )}
      {(isSelected || isHighlighted) && (
        <circle
          r={star.size / 2 + 5}
          stroke="#D9B87A"
          fill="none"
          strokeWidth={1}
          opacity={isSelected ? 0.6 : 0.4}
        />
      )}

      {showTooltip && explanation && (
        <foreignObject x={star.size + 6} y={-30} width={200} height={190} style={{ overflow: "visible" }}>
          <div className="pointer-events-none w-max max-w-[190px] rounded-lg border border-[#3A3560] bg-[#141033]/95 px-3 py-2 shadow-[0_8px_24px_rgba(0,0,0,0.5)] backdrop-blur-sm">
            <p className="text-xs font-medium text-[#F2EDE0]">{star.name}</p>
            {star.hypothesis ? (
              <div className="mt-1 space-y-0.5">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-mono text-[0.6rem] uppercase tracking-wide text-[#6E6A5E]">
                    Confidence
                  </span>
                  <span className="font-mono text-[0.68rem] text-[#D9B87A]">
                    {Math.round(star.hypothesis.confidence * 100)}%
                  </span>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <span className="font-mono text-[0.6rem] uppercase tracking-wide text-[#6E6A5E]">
                    Status
                  </span>
                  <span className="text-[0.68rem] text-[#F2EDE0]">
                    {STATUS_LABEL[star.hypothesis.status] ?? star.hypothesis.status}
                  </span>
                </div>
              </div>
            ) : (
              <p className="mt-1 text-[0.68rem] text-[#6E6A5E]">Not yet explored</p>
            )}

            {!explanation.isLowEvidence && explanation.why.length > 0 && (
              <p className="mt-1.5 text-[0.66rem] leading-relaxed text-[#9C978A]">{explanation.why[0]}</p>
            )}
            {explanation.evidenceLine && (
              <p className="mt-1 font-mono text-[0.56rem] uppercase tracking-wide text-[#6E6A5E]">
                Based on: {explanation.evidenceLine}
              </p>
            )}
            {constellationLabel && (
              <p className="mt-1 text-[0.6rem] italic text-[#6E6A5E]">Part of the {constellationLabel} constellation</p>
            )}
          </div>
        </foreignObject>
      )}
    </motion.g>
  );
}
