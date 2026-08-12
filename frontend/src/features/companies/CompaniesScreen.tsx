import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Building2, ShieldAlert } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { FilterPill } from "../../design-system/components/FilterPill";
import { PageHeader } from "../../design-system/components/PageHeader";
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
  // Loading, a genuine fetch failure, and a genuinely empty catalog for
  // this filter are three different product states.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  const loadCompanies = useCallback(() => {
    setStatus("loading");
    const params = new URLSearchParams();
    if (kind) params.set("organization_kind", kind);
    const qs = params.toString();
    apiClient
      .get<CompaniesResponse>(`/v1/companies${qs ? `?${qs}` : ""}`)
      .then((r) => {
        setCompanies(r.companies);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [kind]);

  useEffect(() => {
    loadCompanies();
  }, [loadCompanies]);

  const kinds = Object.keys(KIND_LABELS);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <PageHeader
        title="Companies"
        description="Real organizations connected to real careers — who hires for what, and where."
      />

      <div className="mt-8">
        <div className="flex flex-wrap gap-1.5">
          <FilterPill active={kind === null} onClick={() => setKind(null)}>
            All
          </FilterPill>
          {kinds.map((k) => (
            <FilterPill key={k} active={kind === k} onClick={() => setKind(k)}>
              {KIND_LABELS[k]}
            </FilterPill>
          ))}
        </div>

        {status === "loading" ? (
          <p className="mt-6 text-sm text-ink-faint">Loading…</p>
        ) : status === "error" ? (
          <div className="mt-6">
            <EmptyStatePanel
              icon={ShieldAlert}
              title="Couldn't Load Companies"
              description="Something went wrong reaching Aureon's servers — this isn't the same as there being no companies. Try again."
              action={<Button variant="secondary" onClick={loadCompanies}>Retry</Button>}
            />
          </div>
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
