import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import { getCurrentStudentId } from "../../shared/config/studentId";
import type { ProjectAttempt, ProjectAttemptEvidenceRequest, ProjectDetail } from "../../shared/api/types";

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

const SUBMISSION_LABELS: Record<string, string> = {
  github_repo: "GitHub repo link",
  writeup: "Link to your write-up (optional)",
  demo_link: "Demo link",
  reflection_only: "Link, if you have one (optional)",
};

/**
 * Sprint 3 — Project detail page, mirroring SkillDetailScreen/
 * CompanyDetailScreen's exact structure (hero / real linked entities),
 * plus an inline completion form — the detail-page-embedded-interaction
 * pattern Experience Lab already uses. The form is deliberately just
 * artifact_url + reflection, never enjoyment/curiosity/persistence
 * flags — Project evidence answers "did you demonstrate this," not
 * "did you enjoy it" (see docs/SPRINT_3.md's Design Checkpoint).
 */
export function ProjectDetailScreen() {
  const { projectId } = useParams<{ projectId: string }>();
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [artifactUrl, setArtifactUrl] = useState("");
  const [reflection, setReflection] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<ProjectAttempt | null>(null);

  useEffect(() => {
    if (!projectId) return;
    setIsLoading(true);
    setResult(null);
    apiClient
      .get<ProjectDetail>(`/v1/projects/${projectId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setIsLoading(false));
  }, [projectId]);

  if (isLoading) {
    return <div className="mx-auto max-w-2xl px-6 py-10 text-sm text-ink-faint">Loading…</div>;
  }

  if (!detail) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="text-sm text-ink-faint">Project not found.</p>
        <Link to="/projects" className="mt-2 inline-block text-sm text-accent-soft">
          Back to Projects
        </Link>
      </div>
    );
  }

  const { project, target_skills: targetSkills, related_careers: relatedCareers, related_companies: relatedCompanies } = detail;
  const hasRealContent = Boolean(artifactUrl.trim()) || Boolean(reflection.trim());

  const submit = async () => {
    setIsSubmitting(true);
    try {
      const body: ProjectAttemptEvidenceRequest = {
        artifact_url: artifactUrl.trim() || null,
        reflection: reflection.trim(),
      };
      const attempt = await apiClient.post<ProjectAttempt>(
        `/v1/students/${getCurrentStudentId()}/projects/${project.id}/complete`,
        body,
      );
      setResult(attempt);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/projects" className="text-xs text-ink-faint transition-colors hover:text-ink-muted">
        ← Back to Projects
      </Link>

      <div className="mt-4">
        <div className="flex flex-wrap items-center gap-1.5">
          <Badge tone="cool">{DIFFICULTY_LABELS[project.difficulty_level] ?? project.difficulty_level}</Badge>
          <Badge tone="neutral">{project.estimated_hours}h estimated</Badge>
        </div>
        <h1 className="mt-2 text-2xl font-light text-ink">{project.title}</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">{project.brief}</p>
      </div>

      {targetSkills.length > 0 && (
        <Surface tone="raised" padding="lg" className="mt-6">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            What This Genuinely Builds
          </p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {targetSkills.map((skill) => (
              <Link key={skill.id} to={`/skills/${skill.id}`}>
                <Badge tone="cool" className="cursor-pointer transition-colors hover:border-accent-soft/40 hover:text-accent-soft">
                  {skill.name}
                </Badge>
              </Link>
            ))}
          </div>
        </Surface>
      )}

      {(relatedCareers.length > 0 || relatedCompanies.length > 0) && (
        <Surface tone="raised" padding="lg" className="mt-4">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Where This Connects</p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {relatedCareers.map((career) => (
              <Link
                key={career.id}
                to={`/explore/career-reality/${career.id}`}
                className="rounded-lg border border-border px-3 py-2 text-sm text-ink transition-colors hover:border-accent-soft/40 hover:text-accent-soft"
              >
                {career.name}
              </Link>
            ))}
            {relatedCompanies.map((company) => (
              <Link
                key={company.id}
                to={`/companies/${company.id}`}
                className="rounded-lg border border-border px-3 py-2 text-sm text-ink transition-colors hover:border-accent-soft/40 hover:text-accent-soft"
              >
                {company.name}
              </Link>
            ))}
          </div>
        </Surface>
      )}

      <Surface tone="raised" padding="lg" className="mt-4 space-y-4">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Mark This Attempted</p>

        {result ? (
          <div className="space-y-2">
            <Badge tone="success">Attempt recorded</Badge>
            <p className="text-sm leading-relaxed text-ink-muted">
              {result.target_skill_ids.length > 0
                ? `This genuinely counts as evidence toward: ${result.target_skill_ids
                    .map((id) => targetSkills.find((s) => s.id === id)?.name ?? id)
                    .join(", ")}.`
                : "Recorded — this project has no linked skills yet, so no skill evidence was added."}
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm leading-relaxed text-ink-muted">
              Share a real artifact and/or a genuine reflection on what you built. Completion alone isn't
              treated as evidence — only real, specific content is.
            </p>
            <input
              type="text"
              value={artifactUrl}
              onChange={(e) => setArtifactUrl(e.target.value)}
              placeholder={SUBMISSION_LABELS[project.submission_type] ?? "Link (optional)"}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-border-strong focus:outline-none"
            />
            <textarea
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
              placeholder="What did you actually build or learn? (optional, but at least one field must be real)"
              rows={4}
              className="w-full resize-none rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-border-strong focus:outline-none"
            />
            <button
              onClick={submit}
              disabled={isSubmitting || !hasRealContent}
              className="rounded-lg bg-accent px-4 py-2 text-xs font-medium tracking-wide text-ink transition-colors hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? "Saving…" : "Mark Attempted"}
            </button>
          </>
        )}
      </Surface>
    </div>
  );
}
