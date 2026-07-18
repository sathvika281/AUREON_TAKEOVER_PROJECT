import { motion } from "framer-motion";
import { BookOpen, Compass, Hammer, MessageCircle, Search, Sparkles } from "lucide-react";

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
      className="flex items-start gap-4 rounded-2xl border border-[#2A2650]/60 bg-[#0C0A22]/80 p-4 text-left shadow-[0_12px_36px_rgba(0,0,0,0.4)] backdrop-blur-md"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#D9B87A]/10 text-[#D9B87A]">
        <Icon size={18} />
      </div>
      <div>
        <p className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-[#D9B87A]/80">{label}</p>
        <h4 className="mt-0.5 font-serif text-base text-[#F2EDE0]">{activity.title}</h4>
        <p className="mt-1 text-xs leading-relaxed text-[#9C978A]">{activity.description}</p>
        <p className="mt-2 text-[0.68rem] italic text-[#6E6A5E]">Why this mission: {activity.reason}</p>
      </div>
    </motion.div>
  );
}
