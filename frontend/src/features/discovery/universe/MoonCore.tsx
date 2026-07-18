import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import type { CareerHypothesis, EvidenceRecord, ReflectionEntry, TraitSignal } from "../../../shared/api/types";
import { EASE_CALM, useReducedMotion } from "../../../design-system/motion";
import { layoutTraits } from "../network/layoutTraits";
import { explainMoon, explainMoonTooltip, explainTrait } from "./explainUniverse";
import { hashToAngle } from "./layoutUniverse";
import { moonLitPath, moonPhaseFor } from "./moonPhases";
import { UniverseTooltip } from "./UniverseTooltip";

const MOON_BASE_RADIUS = 46;
const MOON_MAX_BONUS = 10;
const CRATER_COUNT = 10;

const LIT_COLOR = "#F2EDE0";
const SHADOW_DISC_COLOR = "#141033";
const RIM_COLOR = "#C9C6DA";

function craterLayout(radius: number) {
  return Array.from({ length: CRATER_COUNT }, (_, i) => {
    const angle = hashToAngle(`crater-angle-${i}`);
    const depth = 0.25 + (hashToAngle(`crater-depth-${i}`) % 1) * 0.55;
    const size = 2.5 + (hashToAngle(`crater-size-${i}`) % 1) * 4.5;
    return {
      x: Math.cos(angle) * radius * depth,
      y: Math.sin(angle) * radius * depth,
      r: size,
      opacity: 0.05 + (hashToAngle(`crater-opacity-${i}`) % 1) * 0.06,
    };
  });
}

/**
 * The student — the emotional focal point of the whole scene, per the
 * Identity Discovery redesign's governing hierarchy. A real circular
 * Moon that visibly moves through six real phases (New -> Full) mapped
 * 1:1 from the backend's real understanding_stage, via the classic
 * two-arc lunar-phase path (moonLitPath) rather than a progress bar.
 * Craters are a small, fixed, deterministic set seeded by hashToAngle —
 * the same zero-randomness discipline layoutUniverse.ts already uses —
 * never regenerated, never decorative noise. `glowBoost` (0..1) is the
 * Wow Moment's only hook into this component: a real, rare, externally
 * gated brightening, never a self-triggered idle pulse.
 */
export function MoonCore({
  careerDna,
  confidenceScore,
  understandingStage,
  isThinking,
  glowBoost = 0,
  hypotheses,
  evidenceGraph,
  reflectionJournal,
  dismissToken,
}: {
  careerDna: Record<string, TraitSignal>;
  confidenceScore: number;
  understandingStage: string;
  isThinking: boolean;
  glowBoost?: number;
  hypotheses: CareerHypothesis[];
  evidenceGraph: EvidenceRecord[];
  reflectionJournal: ReflectionEntry[];
  /** Bumped by CareerUniverse whenever the student taps empty space —
   * clears any tap-pinned tooltip here. */
  dismissToken: number;
}) {
  const reduced = useReducedMotion();
  const traitNodes = layoutTraits(careerDna);
  const phase = moonPhaseFor(understandingStage);
  const moonRadius = MOON_BASE_RADIUS + confidenceScore * MOON_MAX_BONUS;
  const litPath = useMemo(() => moonLitPath(moonRadius, phase.litFraction), [moonRadius, phase.litFraction]);
  const craters = useMemo(() => craterLayout(moonRadius), [moonRadius]);
  const clipId = "moon-lit-clip";

  // "moon" is a reserved key for the disc itself; every other key is a
  // real trait name — same hovered/pinned pattern as ConstellationLines.
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);
  const [pinnedKey, setPinnedKey] = useState<string | null>(null);
  useEffect(() => setPinnedKey(null), [dismissToken]);
  const activeKey = hoveredKey ?? pinnedKey;

  const moonSummary = useMemo(
    () => explainMoonTooltip(explainMoon(hypotheses, evidenceGraph, reflectionJournal)),
    [hypotheses, evidenceGraph, reflectionJournal],
  );

  return (
    <g>
      {traitNodes.map((node) => {
        const dist = Math.sqrt(node.x * node.x + node.y * node.y) || 1;
        const ux = node.x / dist;
        const uy = node.y / dist;
        const trimStart = moonRadius + 4;
        const trimEnd = node.size / 5 + 4;
        return (
          <g key={`${node.name}-line`}>
            <motion.line
              x1={0}
              y1={0}
              animate={{ x2: node.x, y2: node.y, opacity: activeKey === node.name ? node.opacity * 0.7 : node.opacity * 0.3 }}
              initial={false}
              transition={{ duration: 0.6, ease: EASE_CALM }}
              stroke="#5B5480"
              strokeWidth={1}
            />
            <line
              x1={ux * trimStart}
              y1={uy * trimStart}
              x2={node.x - ux * trimEnd}
              y2={node.y - uy * trimEnd}
              stroke="transparent"
              strokeWidth={14}
              style={{ cursor: "pointer" }}
              onMouseEnter={() => setHoveredKey(node.name)}
              onMouseLeave={() => setHoveredKey((k) => (k === node.name ? null : k))}
              onClick={() => setPinnedKey((k) => (k === node.name ? null : node.name))}
            />
          </g>
        );
      })}
      {traitNodes.map((node) => (
        <motion.circle
          key={node.name}
          initial={false}
          animate={{ cx: node.x, cy: node.y, r: node.size / 5, opacity: node.opacity }}
          transition={{ duration: 0.6, ease: EASE_CALM }}
          fill="#C9C6DA"
        />
      ))}
      {activeKey &&
        activeKey !== "moon" &&
        traitNodes
          .filter((node) => node.name === activeKey)
          .map((node) => (
            <UniverseTooltip
              key={node.name}
              x={node.x + 12}
              y={node.y - 60}
              explanation={explainTrait(node, evidenceGraph)}
            />
          ))}

      {/* The dark disc — the Moon is always present, even at New Moon. */}
      <circle cx={0} cy={0} r={moonRadius} fill={SHADOW_DISC_COLOR} opacity={0.55} />
      <circle cx={0} cy={0} r={moonRadius} fill="none" stroke={RIM_COLOR} strokeWidth={0.75} opacity={0.22} />
      <circle
        cx={0}
        cy={0}
        r={moonRadius}
        fill="transparent"
        style={{ cursor: "pointer" }}
        onMouseEnter={() => setHoveredKey("moon")}
        onMouseLeave={() => setHoveredKey((k) => (k === "moon" ? null : k))}
        onClick={() => setPinnedKey((k) => (k === "moon" ? null : "moon"))}
      />

      <defs>
        <clipPath id={clipId}>
          <circle cx={0} cy={0} r={moonRadius} />
        </clipPath>
      </defs>

      {/* The real, phase-accurate lit portion. */}
      <motion.path
        d={litPath}
        fill={LIT_COLOR}
        animate={reduced ? { opacity: 0.95 } : { opacity: isThinking ? [0.85, 1, 0.85] : 0.95 + glowBoost * 0.05 }}
        transition={{ duration: 2.2, ease: EASE_CALM, repeat: isThinking && !reduced ? Infinity : 0 }}
        style={{ pointerEvents: "none" }}
      />

      <g clipPath={`url(#${clipId})`} opacity={0.5 + phase.litFraction * 0.5} style={{ pointerEvents: "none" }}>
        {craters.map((c, i) => (
          <ellipse key={i} cx={c.x} cy={c.y} rx={c.r} ry={c.r * 0.8} fill="#8B87A6" opacity={c.opacity} />
        ))}
      </g>

      {activeKey === "moon" && <UniverseTooltip x={moonRadius + 16} y={-moonRadius} explanation={moonSummary} />}
    </g>
  );
}
