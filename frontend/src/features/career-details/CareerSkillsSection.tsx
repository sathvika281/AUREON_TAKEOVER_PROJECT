import { Link } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Surface } from "../../design-system/components/Surface";
import type { Skill } from "../../shared/api/types";

const CATEGORY_LABELS: Record<string, string> = {
  technical: "Technical",
  domain_knowledge: "Domain Knowledge",
  soft_skill: "Soft Skill",
  tool: "Tool",
};

/**
 * Sprint 1 — real, linked Skill entities for this career (from the new
 * `required_skill_ids` edge). Deliberately additive alongside
 * RealitySection's existing plain-text "Required skills" list (untouched,
 * still reads directly from `reality.required_skills`) rather than
 * replacing it — this section only renders once a career has been
 * backfilled with real Skill links, per docs/SPRINT_1.md's scope.
 */
export function CareerSkillsSection({ skills }: { skills: Skill[] }) {
  if (skills.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-3">
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
        Skills, connected to what you can actually build
      </p>
      <div className="flex flex-wrap gap-1.5">
        {skills.map((skill) => (
          <Link key={skill.id} to={`/skills/${skill.id}`}>
            <Badge tone="cool" className="cursor-pointer transition-colors hover:border-accent-soft/40 hover:text-accent-soft">
              {skill.name}
              <span className="text-ink-faint"> · {CATEGORY_LABELS[skill.category] ?? skill.category}</span>
            </Badge>
          </Link>
        ))}
      </div>
    </Surface>
  );
}
