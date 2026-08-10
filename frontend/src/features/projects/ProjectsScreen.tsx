import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Hammer } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { Project, ProjectsResponse } from "../../shared/api/types";

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

/**
 * Sprint 3 — Project Knowledge Base browse page. Same structural pattern
 * as SkillsScreen/CompaniesScreen (filter chips, loading/empty states) —
 * the proven Sprint 1/2 shape, reused rather than reinvented.
 */
export function ProjectsScreen() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [difficulty, setDifficulty] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (difficulty) params.set("difficulty_level", difficulty);
    const qs = params.toString();
    apiClient
      .get<ProjectsResponse>(`/v1/projects${qs ? `?${qs}` : ""}`)
      .then((r) => setProjects(r.projects))
      .catch(() => setProjects([]))
      .finally(() => setIsLoading(false));
  }, [difficulty]);

  const difficulties = Object.keys(DIFFICULTY_LABELS);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Projects</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Real, attemptable builds — the bridge between learning a skill and demonstrating it.
      </p>

      <div className="mt-8">
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setDifficulty(null)}
            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
              difficulty === null
                ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
            }`}
          >
            All
          </button>
          {difficulties.map((d) => (
            <button
              key={d}
              onClick={() => setDifficulty(d)}
              className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                difficulty === d
                  ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                  : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
              }`}
            >
              {DIFFICULTY_LABELS[d]}
            </button>
          ))}
        </div>

        {isLoading ? (
          <p className="mt-6 text-sm text-ink-faint">Loading…</p>
        ) : projects.length === 0 ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={Hammer}
              title="No Projects Here Yet"
              description="Aureon's Project knowledge base hasn't been populated for this difficulty yet."
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {projects.map((project) => (
              <Link key={project.id} to={`/projects/${project.id}`}>
                <Surface
                  tone="raised"
                  padding="md"
                  className="h-full transition-colors hover:border-accent-soft/40"
                >
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                    {DIFFICULTY_LABELS[project.difficulty_level] ?? project.difficulty_level}
                    {" · "}
                    {project.estimated_hours}h
                  </p>
                  <p className="mt-1 text-sm font-medium text-ink">{project.title}</p>
                  <p className="mt-1 text-xs leading-relaxed text-ink-muted">{project.brief}</p>
                </Surface>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
