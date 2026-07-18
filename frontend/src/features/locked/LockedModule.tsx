import { motion } from "framer-motion";
import { Lock } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { EASE_CALM } from "../../design-system/motion";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import type { ModuleEntry } from "../navigation/journeyConfig";

/**
 * Shared by every module whose backing agent is still a stub (Skill Gap,
 * Roadmap, Opportunity Graph). Never "Coming Soon" — a full workspace that
 * teaches what the module does and why it's worth waiting for, built from
 * the module's own config rather than fabricated content. Real Discovery
 * progress (confidence, stage) is shown as honest context, not a claim
 * about an exact unlock threshold that doesn't exist yet.
 */
export function LockedModule({ module }: { module: ModuleEntry }) {
  const Icon = module.icon;
  const { confidenceScore, understandingStage } = useDiscoveryContext();

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: EASE_CALM }}
      >
        <Surface tone="raised" padding="lg">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-border bg-surface text-ink-faint">
              <Icon size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-medium text-ink">{module.title}</h1>
                <Badge tone="cool">
                  <Lock size={10} className="mr-1" />
                  Locked
                </Badge>
              </div>
              {module.lockedDescription && (
                <p className="mt-1 text-sm leading-relaxed text-ink-muted">{module.lockedDescription}</p>
              )}
            </div>
          </div>

          <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Your Discovery Progress</p>
              <p className="mt-1 text-sm text-ink-muted">{understandingStage}</p>
            </div>
            <div className="h-1 w-32 overflow-hidden rounded-full bg-white/5">
              <div
                className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out"
                style={{ width: `${Math.round(confidenceScore * 100)}%` }}
              />
            </div>
          </div>
        </Surface>
      </motion.div>

      {module.lockedSteps && module.lockedSteps.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: EASE_CALM, delay: 0.1 }}
          className="mt-6"
        >
          <ProcessSteps title="What This Will Do" steps={module.lockedSteps} />
        </motion.div>
      )}

      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: EASE_CALM, delay: 0.2 }}
        className="mt-6 text-center text-xs leading-relaxed text-ink-faint"
      >
        {module.lockedCopy}
      </motion.p>
    </div>
  );
}
