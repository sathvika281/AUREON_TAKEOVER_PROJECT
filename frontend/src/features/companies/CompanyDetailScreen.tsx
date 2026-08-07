import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { CompanyDetail } from "../../shared/api/types";
import { CompanyLogo } from "./CompanyLogo";

const KIND_LABELS: Record<string, string> = {
  company: "Company",
  nonprofit: "Nonprofit",
  government: "Government",
  university: "University",
  community: "Community",
};

const SIZE_LABELS: Record<string, string> = {
  startup: "Startup",
  mid_size: "Mid-size",
  enterprise: "Enterprise",
};

/**
 * Sprint 2 — Company detail page, mirroring SkillDetailScreen's exact
 * structure (hero / where it connects / real requiring careers).
 */
export function CompanyDetailScreen() {
  const { companyId } = useParams<{ companyId: string }>();
  const [detail, setDetail] = useState<CompanyDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!companyId) return;
    setIsLoading(true);
    apiClient
      .get<CompanyDetail>(`/v1/companies/${companyId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setIsLoading(false));
  }, [companyId]);

  if (isLoading) {
    return <div className="mx-auto max-w-2xl px-6 py-10 text-sm text-ink-faint">Loading…</div>;
  }

  if (!detail) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="text-sm text-ink-faint">Company not found.</p>
        <Link to="/companies" className="mt-2 inline-block text-sm text-accent-soft">
          Back to Companies
        </Link>
      </div>
    );
  }

  const { company, careers_hiring_from_it: careersHiringFromIt } = detail;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/companies" className="text-xs text-ink-faint transition-colors hover:text-ink-muted">
        ← Back to Companies
      </Link>

      <div className="mt-4 flex items-start gap-4">
        <CompanyLogo company={company} size={56} />
        <div>
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge tone="cool">{KIND_LABELS[company.organization_kind] ?? company.organization_kind}</Badge>
            {company.size_category && <Badge tone="neutral">{SIZE_LABELS[company.size_category] ?? company.size_category}</Badge>}
          </div>
          <h1 className="mt-2 text-2xl font-light text-ink">{company.name}</h1>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">{company.what_they_do}</p>
        </div>
      </div>

      {company.notable_for && (
        <p className="mt-4 border-l border-border pl-3 text-sm italic leading-relaxed text-ink-muted">
          {company.notable_for}
        </p>
      )}

      {company.hiring_focus_areas.length > 0 && (
        <Surface tone="raised" padding="lg" className="mt-6">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">What They Hire For</p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {company.hiring_focus_areas.map((area) => (
              <Badge key={area} tone="cool">{area}</Badge>
            ))}
          </div>
        </Surface>
      )}

      {careersHiringFromIt.length > 0 && (
        <Surface tone="raised" padding="lg" className="mt-4">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            Careers That Hire Here
          </p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {careersHiringFromIt.map((career) => (
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

      {careersHiringFromIt.length === 0 && company.hiring_focus_areas.length === 0 && (
        <p className="mt-6 text-sm italic leading-relaxed text-ink-faint">
          This company is still being connected — no careers or hiring focus areas linked yet.
        </p>
      )}
    </div>
  );
}
