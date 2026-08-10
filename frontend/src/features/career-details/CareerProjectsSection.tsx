import { Link } from "react-router-dom";

import { Surface } from "../../design-system/components/Surface";
import type { Project } from "../../shared/api/types";

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

/**
 * Sprint 3 — real, linked Project entities for this career (from
 * Project's own `related_career_ids` edge — Project holds the edge,
 * not Career, unlike Skill/Company). Additive alongside the existing
 * plain-text "Projects" list rendered elsewhere on this page (untouched)
 * — same discipline as CareerSkillsSection/CareerCompaniesSection.
 */
export function CareerProjectsSection({ projects }: { projects: Project[] }) {
  if (projects.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-3">
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
        Projects that build toward this career
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {projects.map((project) => (
          <Link
            key={project.id}
            to={`/projects/${project.id}`}
            className="rounded-lg border border-border px-3 py-2 transition-colors hover:border-accent-soft/40"
          >
            <p className="text-sm text-ink">{project.title}</p>
            <p className="mt-0.5 text-xs text-ink-faint">
              {DIFFICULTY_LABELS[project.difficulty_level] ?? project.difficulty_level} · {project.estimated_hours}h
            </p>
          </Link>
        ))}
      </div>
    </Surface>
  );
}
