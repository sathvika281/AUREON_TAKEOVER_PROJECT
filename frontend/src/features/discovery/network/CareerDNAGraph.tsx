import { motion } from "framer-motion";

import type { TraitSignal } from "../../../shared/api/types";
import { EASE_CALM, useReducedMotion } from "../../../design-system/motion";
import { layoutTraits } from "./layoutTraits";

const CONTAINER_SIZE = 480;

/**
 * Career DNA as a calm, spatial layout — the arrangement of traits
 * around a center is real, data-driven visualization (see layoutTraits),
 * not decoration. No glow, no blur, no spring bounce: nodes fade and
 * settle into position with the same calm easing as everything else.
 */
export function CareerDNAGraph({
  careerDna,
  isThinking,
  stillness = false,
}: {
  careerDna: Record<string, TraitSignal>;
  isThinking: boolean;
  stillness?: boolean;
}) {
  const reduced = useReducedMotion();
  const nodes = layoutTraits(careerDna);

  return (
    <div
      className="relative mx-auto"
      style={{ width: CONTAINER_SIZE, height: CONTAINER_SIZE }}
    >
      <svg
        className="pointer-events-none absolute inset-0 h-full w-full overflow-visible"
        aria-hidden="true"
      >
        <g transform={`translate(${CONTAINER_SIZE / 2}, ${CONTAINER_SIZE / 2})`}>
          {nodes.map((node) => (
            <motion.line
              key={node.name}
              x1={0}
              y1={0}
              animate={{ x2: node.x, y2: node.y, opacity: node.opacity * 0.4 }}
              initial={false}
              transition={{ duration: 0.6, ease: EASE_CALM }}
              stroke="#2a2a2a"
              strokeWidth={1}
            />
          ))}
        </g>
      </svg>

      <motion.div
        className="absolute left-1/2 top-1/2 flex h-20 w-20 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-accent/40 bg-accent/10 text-xs font-medium uppercase tracking-widest text-accent-soft"
        animate={reduced ? undefined : { opacity: isThinking && !stillness ? [0.7, 1, 0.7] : 1 }}
        transition={{ duration: 1.8, ease: EASE_CALM, repeat: isThinking && !stillness && !reduced ? Infinity : 0 }}
      >
        You
      </motion.div>

      {nodes.map((node) => (
        <motion.div
          key={node.name}
          initial={false}
          animate={{
            x: node.x - node.size / 2,
            y: node.y - node.size / 2,
            width: node.size,
            height: node.size,
            opacity: node.opacity,
          }}
          transition={{ duration: 0.6, ease: EASE_CALM }}
          className="group absolute left-1/2 top-1/2 flex items-center justify-center rounded-full border border-border bg-surface text-center"
        >
          <span className="pointer-events-none select-none px-1 text-[0.65rem] leading-tight text-ink-muted transition group-hover:text-ink">
            {node.label}
          </span>
        </motion.div>
      ))}
    </div>
  );
}
