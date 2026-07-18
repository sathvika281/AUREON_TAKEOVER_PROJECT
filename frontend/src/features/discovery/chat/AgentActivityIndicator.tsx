import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * Names real backend concepts (Discovery Agent, Evidence Engine,
 * Hypothesis Engine, and the Planner all genuinely run every turn) —
 * this translates real backend work into human language rather than
 * fabricating technical claims. Cycles for as long as a request is in
 * flight; there's no per-step event feed from the backend, so this is a
 * presentational pace, not a literal step tracker.
 */
const LABELS = [
  "Discovery Agent — understanding what matters to you…",
  "Evidence Engine — weighing what's been said…",
  "Hypothesis Engine — testing a few directions…",
  "Planner — choosing the next best question…",
];

export function AgentActivityIndicator() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % LABELS.length);
    }, 1700);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-4 items-center justify-center overflow-hidden font-mono text-xs text-[#6E6A5E]">
      <AnimatePresence mode="wait">
        <motion.span
          key={index}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.4 }}
        >
          {LABELS[index]}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
