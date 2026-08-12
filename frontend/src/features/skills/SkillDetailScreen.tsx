import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ShieldAlert } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { ApiError, apiClient } from "../../shared/api/client";
import type { SkillDetail } from "../../shared/api/types";

const CATEGORY_LABELS: Record<string, string> = {
  technical: "Technical",
  domain_knowledge: "Domain Knowledge",
  soft_skill: "Soft Skill",
  tool: "Tool",
};

/**
 * Sprint 1 — Skill detail page, per docs/AUREON_DATA_ARCHITECTURE.md §3's
 * UI Representation (hero / where-it's-used / how-to-build-it), scoped to
 * what actually exists this sprint. "How to build it" uses the real
 * `evidence_types_that_count` field rather than Learning Resource links —
 * that entity doesn't exist yet (explicitly out of scope, see
 * docs/SPRINT_1.md) and fabricating resource links here would violate
 * the same honesty discipline this whole model is built on.
 */
export function SkillDetailScreen() {
  const { skillId } = useParams<{ skillId: string }>();
  const [detail, setDetail] = useState<SkillDetail | null>(null);
  // A skill genuinely not existing and a request that failed to reach
  // Aureon's servers are different states — the former is a dead link,
  // the latter is worth retrying.
  const [status, setStatus] = useState<"loading" | "success" | "not-found" | "error">("loading");

  const loadDetail = useCallback(() => {
    if (!skillId) return;
    setStatus("loading");
    apiClient
      .get<SkillDetail>(`/v1/skills/${skillId}`)
      .then((r) => {
        setDetail(r);
        setStatus("success");
      })
      .catch((err) => setStatus(err instanceof ApiError && err.status === 404 ? "not-found" : "error"));
  }, [skillId]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  if (status === "loading") {
    return <div className="mx-auto max-w-2xl px-6 py-10 text-sm text-ink-faint">Loading…</div>;
  }

  if (status === "not-found") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="text-sm text-ink-faint">Skill not found.</p>
        <Link to="/skills" className="mt-2 inline-block text-sm text-accent-soft">
          Back to Skills
        </Link>
      </div>
    );
  }

  if (status === "error" || !detail) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <EmptyStatePanel
          icon={ShieldAlert}
          title="Couldn't Load This Skill"
          description="Something went wrong reaching Aureon's servers — this isn't the same as the skill not existing. Try again."
          action={<Button variant="secondary" onClick={loadDetail}>Retry</Button>}
        />
      </div>
    );
  }

  const { skill, careers_requiring_it: careersRequiringIt } = detail;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/skills" className="text-xs text-ink-faint transition-colors hover:text-ink-muted">
        ← Back to Skills
      </Link>

      <div className="mt-4">
        <Badge tone="cool">{CATEGORY_LABELS[skill.category] ?? skill.category}</Badge>
        <h1 className="mt-2 text-2xl font-light text-ink">{skill.name}</h1>
        <p className="mt-2 text-sm leading-relaxed text-ink-muted">{skill.description}</p>
      </div>

      {careersRequiringIt.length > 0 && (
        <Surface tone="raised" padding="lg" className="mt-6">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            Careers That Require This
          </p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {careersRequiringIt.map((career) => (
              <Link
                key={career.id}
                to={`/explore/career-reality/${career.id}`}
                className="rounded-lg border border-border px-3 py-2 text-sm text-ink transition-colors hover:border-accent-soft/40 hover:text-accent-soft"
              >
                {career.name}
              </Link>
            ))}
          </div>
        </Surface>
      )}

      {skill.evidence_types_that_count.length > 0 && (
        <Surface tone="raised" padding="lg" className="mt-4">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            What Honestly Counts as Real Evidence
          </p>
          <ul className="mt-3 space-y-1.5">
            {skill.evidence_types_that_count.map((item) => (
              <li key={item} className="text-sm leading-relaxed text-ink-muted">
                · {item}
              </li>
            ))}
          </ul>
        </Surface>
      )}

      {careersRequiringIt.length === 0 && skill.evidence_types_that_count.length === 0 && (
        <p className="mt-6 text-sm italic leading-relaxed text-ink-faint">
          This skill is still being connected — no careers or evidence types linked yet.
        </p>
      )}
    </div>
  );
}
