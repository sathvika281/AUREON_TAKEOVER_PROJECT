import { motion } from "framer-motion";
import { useState } from "react";

import { EASE_CALM } from "../../../design-system/motion";
import type { HiddenPotentialPattern } from "../../../shared/api/types";
import { hashToAngle } from "./layoutUniverse";

const AMBIENT_RADIUS = 170;

/**
 * Hidden Potential — one distinct, interactive "clearing" per real
 * HiddenPotentialPattern the backend has actually found; its hover text
 * is always the real generated `sentence`, never invented. No ambient
 * decoration: the scene's background stays a single flat shade
 * everywhere the backend hasn't actually found something.
 */
export function NebulaCloud({
  patterns,
}: {
  patterns: HiddenPotentialPattern[];
}) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <g>
      {patterns.map((pattern) => {
        const angle = hashToAngle(pattern.id);
        const x = Math.cos(angle) * (AMBIENT_RADIUS + 40);
        const y = Math.sin(angle) * (AMBIENT_RADIUS + 40);
        const isHovered = hoveredId === pattern.id;
        return (
          <g
            key={pattern.id}
            onMouseEnter={() => setHoveredId(pattern.id)}
            onMouseLeave={() => setHoveredId(null)}
            style={{ cursor: "default" }}
          >
            <motion.circle
              cx={x}
              cy={y}
              r={38}
              fill="#9B7FD4"
              animate={{ opacity: isHovered ? 0.32 : 0.18 }}
              style={{ filter: "blur(3px)" }}
              transition={{ duration: 0.6, ease: EASE_CALM }}
            />
            {isHovered && (
              <motion.text
                x={x}
                y={y - 48}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.4, ease: EASE_CALM }}
                textAnchor="middle"
                fill="#9C978A"
                className="text-[10px]"
              >
                {pattern.sentence.length > 60 ? `${pattern.sentence.slice(0, 60)}…` : pattern.sentence}
              </motion.text>
            )}
          </g>
        );
      })}
    </g>
  );
}
