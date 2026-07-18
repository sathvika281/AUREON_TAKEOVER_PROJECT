import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import { EASE_CALM } from "../../../design-system/motion";
import { explainConstellationLine, titleCase } from "./explainUniverse";
import type { Constellation, UniverseStar } from "./layoutUniverse";
import { UniverseTooltip } from "./UniverseTooltip";

/** Trim a segment's hit-stroke inward from both ends so it never overlaps
 * a star's own hit circle (Star.tsx's invisible hit circle is
 * `max(star.size, 10)`) — prevents two tooltips firing at once near a
 * line/star junction without needing global hover-state coordination. */
function trimSegment(star: UniverseStar, next: UniverseStar) {
  const dx = next.x - star.x;
  const dy = next.y - star.y;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  const trimA = Math.max(star.size, 10) + 4;
  const trimB = Math.max(next.size, 10) + 4;
  return {
    x1: star.x + ux * trimA,
    y1: star.y + uy * trimA,
    x2: next.x - ux * trimB,
    y2: next.y - uy * trimB,
  };
}

/**
 * Faint connecting lines within a real `industry` group, revealed only
 * once confidenceScore crosses the progressive-disclosure thresholds in
 * layoutUniverse.ts — discovery organizing itself gradually, not all at
 * once. Now explainable: hovering (desktop) or tapping (mobile) a segment
 * shows the real, honest reason two careers are grouped together, and
 * highlights both endpoint stars via `onHoverLine`.
 */
export function ConstellationLines({
  constellations,
  stars,
  dismissToken,
  onHoverLine,
}: {
  constellations: Constellation[];
  stars: UniverseStar[];
  /** Bumped by CareerUniverse whenever the student taps empty space —
   * clears any tap-pinned tooltip here. */
  dismissToken: number;
  onHoverLine?: (ids: [string, string] | null) => void;
}) {
  const byId = new Map(stars.map((s) => [s.id, s]));
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);
  const [pinnedKey, setPinnedKey] = useState<string | null>(null);

  useEffect(() => {
    setPinnedKey(null);
  }, [dismissToken]);

  const activeKey = hoveredKey ?? pinnedKey;

  useEffect(() => {
    if (!onHoverLine) return;
    if (!activeKey) {
      onHoverLine(null);
      return;
    }
    const [a, b] = activeKey.split("::");
    onHoverLine([a, b]);
  }, [activeKey, onHoverLine]);

  return (
    <>
      {constellations.map((constellation) => {
        if (!constellation.showLines) return null;
        const members = constellation.connectedStarIds
          .map((id) => byId.get(id))
          .filter((s): s is UniverseStar => !!s);
        if (members.length < 2) return null;

        return (
          <g key={constellation.industry}>
            {members.map((star, i) => {
              const next = members[(i + 1) % members.length];
              if (i === members.length - 1) return null;
              const key = `${star.id}::${next.id}`;
              const isActive = activeKey === key;
              const explanation = isActive ? explainConstellationLine(star, next, constellation.industry) : null;
              const hit = trimSegment(star, next);
              const midX = (star.x + next.x) / 2;
              const midY = (star.y + next.y) / 2;

              return (
                <g key={key}>
                  <motion.line
                    animate={{ x1: star.x, y1: star.y, x2: next.x, y2: next.y, opacity: isActive ? 0.55 : 0.24 }}
                    initial={false}
                    transition={{ duration: 0.4, ease: EASE_CALM }}
                    stroke="#D9B87A"
                    strokeWidth={1}
                  />
                  <line
                    x1={hit.x1}
                    y1={hit.y1}
                    x2={hit.x2}
                    y2={hit.y2}
                    stroke="transparent"
                    strokeWidth={16}
                    style={{ cursor: "pointer" }}
                    onMouseEnter={() => setHoveredKey(key)}
                    onMouseLeave={() => setHoveredKey((k) => (k === key ? null : k))}
                    onClick={() => setPinnedKey((k) => (k === key ? null : key))}
                  />
                  {isActive && explanation && (
                    <UniverseTooltip x={midX + 10} y={midY - 60} explanation={explanation} />
                  )}
                </g>
              );
            })}
            {constellation.showLabel && (
              <g
                style={{ cursor: "pointer" }}
                onMouseEnter={() => setHoveredKey(`${members[0].id}::${members[1].id}`)}
                onMouseLeave={() =>
                  setHoveredKey((k) => (k === `${members[0].id}::${members[1].id}` ? null : k))
                }
                onClick={() =>
                  setPinnedKey((k) => (k === `${members[0].id}::${members[1].id}` ? null : `${members[0].id}::${members[1].id}`))
                }
              >
                <motion.text
                  animate={{ x: constellation.centroid.x, y: constellation.centroid.y - 24, opacity: 0.6 }}
                  initial={false}
                  transition={{ duration: 1, ease: EASE_CALM }}
                  fill="#D9B87A"
                  className="font-mono text-[9px] uppercase tracking-[0.16em]"
                  textAnchor="middle"
                >
                  {titleCase(constellation.industry)}
                </motion.text>
              </g>
            )}
          </g>
        );
      })}
    </>
  );
}
