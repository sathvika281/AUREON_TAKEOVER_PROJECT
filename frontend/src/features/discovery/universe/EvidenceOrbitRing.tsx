import { motion } from "framer-motion";
import { useState } from "react";

import { EASE_CALM, useReducedMotion } from "../../../design-system/motion";
import { matchEvidenceIcon } from "./evidenceMissionCopy";
import type { EvidenceOrbit } from "./layoutUniverse";

const ORBIT_SECONDS_BASE = 90;
const ORBIT_SECONDS_STEP = 12;

/**
 * A satellite — real evidence, orbiting. One per real Discovery Notebook
 * source; the ring is a faint orbit guide (thickness/opacity scale with
 * the real entry count), the small bright body is the satellite itself,
 * continuously orbiting because that is what a satellite does — not a
 * decorative idle animation, the one physically-motivated exception to
 * "motion only on real data change" (its existence, size, and orbital
 * radius are still 100% real). The hover tooltip shows the real count
 * plus the real most-recent entry text, never placeholder copy.
 */
export function EvidenceOrbitRing({ orbit, index }: { orbit: EvidenceOrbit; index: number }) {
  const [isHovered, setIsHovered] = useState(false);
  const reduced = useReducedMotion();
  const opacity = Math.min(0.1 + orbit.count * 0.04, 0.4);
  const strokeWidth = Math.min(0.5 + orbit.count * 0.2, 2);
  const satelliteSize = Math.min(2.2 + orbit.count * 0.5, 5.5);
  const orbitSeconds = ORBIT_SECONDS_BASE + index * ORBIT_SECONDS_STEP;
  const Icon = matchEvidenceIcon(orbit.key);

  return (
    <g onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
      <motion.circle
        cx={0}
        cy={0}
        r={orbit.radius}
        fill="none"
        stroke="#6E6A5E"
        animate={{ opacity: isHovered ? opacity + 0.18 : opacity, strokeWidth }}
        transition={{ duration: 0.7, ease: EASE_CALM }}
        style={{ cursor: "default" }}
      />

      <motion.g
        style={{ transformOrigin: "0px 0px" }}
        animate={reduced ? undefined : { rotate: 360 }}
        transition={reduced ? undefined : { duration: orbitSeconds, ease: "linear", repeat: Infinity }}
      >
        <circle cx={orbit.radius} cy={0} r={satelliteSize} fill="#F2EDE0" opacity={0.85} />
        <circle cx={orbit.radius} cy={0} r={satelliteSize + 3} fill="#F2EDE0" opacity={0.18} />
      </motion.g>

      {isHovered && (
        <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
          {Icon && (
            <foreignObject x={-8} y={-orbit.radius - 24} width={16} height={16} style={{ overflow: "visible" }}>
              <div className="flex items-center justify-center text-[#F2EDE0]">
                <Icon size={12} />
              </div>
            </foreignObject>
          )}
          <text x={0} y={-orbit.radius - 6} textAnchor="middle" fill="#F2EDE0" className="text-[10px] font-medium">
            {orbit.label} · {orbit.count}
          </text>
          {orbit.latestText && (
            <text x={0} y={-orbit.radius + 8} textAnchor="middle" fill="#8C877A" className="text-[9px]">
              {orbit.latestText.length > 50 ? `${orbit.latestText.slice(0, 50)}…` : orbit.latestText}
            </text>
          )}
        </motion.g>
      )}
    </g>
  );
}
