import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Building2 } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { Company, CompaniesResponse } from "../../shared/api/types";
import { CompanyLogo } from "./CompanyLogo";

const KIND_LABELS: Record<string, string> = {
  company: "Company",
  nonprofit: "Nonprofit",
  government: "Government",
  university: "University",
  community: "Community",
};

/**
 * Sprint 2 — Company Knowledge Base browse page. Same structural pattern
 * as SkillsScreen (category/kind filter chips, loading/empty states) —
 * the proven Sprint 1 shape, reused rather than reinvented.
 */
export function CompaniesScreen() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [kind, setKind] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (kind) params.set("organization_kind", kind);
    const qs = params.toString();
    apiClient
      .get<CompaniesResponse>(`/v1/companies${qs ? `?${qs}` : ""}`)
      .then((r) => setCompanies(r.companies))
      .catch(() => setCompanies([]))
      .finally(() => setIsLoading(false));
  }, [kind]);

  const kinds = Object.keys(KIND_LABELS);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Companies</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Real organizations connected to real careers — who hires for what, and where.
      </p>

      <div className="mt-8">
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setKind(null)}
            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
              kind === null
                ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
            }`}
          >
            All
          </button>
          {kinds.map((k) => (
            <button
              key={k}
              onClick={() => setKind(k)}
              className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                kind === k
                  ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                  : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
              }`}
            >
              {KIND_LABELS[k]}
            </button>
          ))}
        </div>

        {isLoading ? (
          <p className="mt-6 text-sm text-ink-faint">Loading…</p>
        ) : companies.length === 0 ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={Building2}
              title="No Companies Here Yet"
              description="Aureon's Company knowledge base hasn't been populated for this category yet."
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {companies.map((company) => (
              <Link key={company.id} to={`/companies/${company.id}`}>
                <Surface
                  tone="raised"
                  padding="md"
                  className="flex h-full items-start gap-3 transition-colors hover:border-accent-soft/40"
                >
                  <CompanyLogo company={company} size={36} />
                  <div>
                    <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                      {KIND_LABELS[company.organization_kind] ?? company.organization_kind}
                    </p>
                    <p className="mt-1 text-sm font-medium text-ink">{company.name}</p>
                    <p className="mt-1 text-xs leading-relaxed text-ink-muted">{company.what_they_do}</p>
                  </div>
                </Surface>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
