/**
 * Presentation-only mapping over the backend's real 6-value
 * understanding_stage literal (backend/.../discovery/understanding_level.py).
 * The technical name always stays visible in parens — this never
 * replaces the real value, only softens how it reads.
 */
const MILESTONE_COPY: Record<string, string> = {
  Seed: "Beginning Exploration",
  Explorer: "Gathering First Signals",
  "Patterns Emerging": "Building Connections",
  "Identity Taking Shape": "Forming a Fuller Picture",
  "Career DNA Forming": "Understanding You",
  "Decision Ready": "Ready to Explore Direction",
};

export function humanizeMilestone(stage: string): { friendly: string; technical: string } {
  return {
    friendly: MILESTONE_COPY[stage] ?? stage,
    technical: stage,
  };
}
