import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Wrench } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { FilterPill } from "../../design-system/components/FilterPill";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { Skill, SkillsResponse } from "../../shared/api/types";

const CATEGORY_LABELS: Record<string, string> = {
  technical: "Technical",
  domain_knowledge: "Domain Knowledge",
  soft_skill: "Soft Skill",
  tool: "Tool",
};

/**
 * Sprint 1 — Skill Knowledge Base browse page. Same structural pattern as
 * GlobalTrendsScreen (category filter chips, loading/empty states) —
 * deliberately not a new visual language, per docs/SPRINT_1.md's "we are
 * not redesigning the UI" scope.
 */
export function SkillsScreen() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [category, setCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    const qs = params.toString();
    apiClient
      .get<SkillsResponse>(`/v1/skills${qs ? `?${qs}` : ""}`)
      .then((r) => setSkills(r.skills))
      .catch(() => setSkills([]))
      .finally(() => setIsLoading(false));
  }, [category]);

  const categories = Object.keys(CATEGORY_LABELS);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Skills</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Real, connective skills — what careers actually require, and how to genuinely build each one.
      </p>

      <div className="mt-8">
        <div className="flex flex-wrap gap-1.5">
          <FilterPill active={category === null} onClick={() => setCategory(null)}>
            All
          </FilterPill>
          {categories.map((c) => (
            <FilterPill key={c} active={category === c} onClick={() => setCategory(c)}>
              {CATEGORY_LABELS[c]}
            </FilterPill>
          ))}
        </div>

        {isLoading ? (
          <p className="mt-6 text-sm text-ink-faint">Loading…</p>
        ) : skills.length === 0 ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={Wrench}
              title="No Skills Here Yet"
              description="Aureon's Skill knowledge base hasn't been populated for this category yet."
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {skills.map((skill) => (
              <Link key={skill.id} to={`/skills/${skill.id}`}>
                <Surface
                  tone="raised"
                  padding="md"
                  className="h-full transition-colors hover:border-accent-soft/40"
                >
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                    {CATEGORY_LABELS[skill.category] ?? skill.category}
                  </p>
                  <p className="mt-1 text-sm font-medium text-ink">{skill.name}</p>
                  <p className="mt-1 text-xs leading-relaxed text-ink-muted">{skill.description}</p>
                </Surface>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
