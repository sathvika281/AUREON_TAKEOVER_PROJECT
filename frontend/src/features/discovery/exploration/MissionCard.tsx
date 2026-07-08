import { motion } from "framer-motion";
import { BookOpen, Compass, Hammer, MessageCircle, Search, Sparkles } from "lucide-react";

import { Surface } from "../../../design-system/components/Surface";
import { EASE_CALM } from "../../../design-system/motion";
import type { SuggestedActivity } from "../../../shared/api/types";

const CATEGORY_RULES: Array<{ pattern: RegExp; icon: typeof Compass; label: string }> = [
  { pattern: /\b(build|make|create|design|prototype)\b/i, icon: Hammer, label: "Mini Challenge" },
  { pattern: /\b(research|read|article|learn about)\b/i, icon: BookOpen, label: "Experiment" },
  { pattern: /\b(interview|talk to|ask someone|conversation)\b/i, icon: MessageCircle, label: "Mission" },
  { pattern: /\b(explore|look into|investigate|try)\b/i, icon: Search, label: "Observation" },
  { pattern: /\b(reflect|think about|consider|journal)\b/i, icon: Sparkles, label: "Observation" },
];

function categoryFor(text: string) {
  const match = CATEGORY_RULES.find((rule) => rule.pattern.test(text));
  return match ?? { icon: Compass, label: "Mission" };
}

/**
 * Exploration should feel like receiving a mission, not homework. The
 * backend only ever returns one real field here (suggested_activity,
 * title + description) — the category label varies the presentation via
 * a real keyword heuristic over that same text, not invented structure.
 */
export function MissionCard({ activity }: { activity: SuggestedActivity }) {
  const { icon: Icon, label } = categoryFor(`${activity.title} ${activity.description}`);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: EASE_CALM }}
    >
      <Surface tone="raised" padding="md" className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Icon size={18} />
        </div>
        <div>
          <p className="text-[0.68rem] uppercase tracking-widest text-accent/80">{label}</p>
          <h4 className="mt-0.5 text-sm font-medium text-ink">{activity.title}</h4>
          <p className="mt-1 text-xs leading-relaxed text-ink-muted">{activity.description}</p>
          <p className="mt-2 text-[0.68rem] italic text-ink-faint">Why this mission: {activity.reason}</p>
        </div>
      </Surface>
    </motion.div>
  );
}
