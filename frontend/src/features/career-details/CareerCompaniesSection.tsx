import { Link } from "react-router-dom";

import { Surface } from "../../design-system/components/Surface";
import { CompanyLogo } from "../companies/CompanyLogo";
import type { Company } from "../../shared/api/types";

/**
 * Sprint 2 — real, linked Company entities for this career (from the new
 * `company_ids` edge). Additive alongside the existing plain-text
 * "Companies" list rendered elsewhere on this page (untouched) — same
 * discipline as CareerSkillsSection in Sprint 1.
 */
export function CareerCompaniesSection({ companies }: { companies: Company[] }) {
  if (companies.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-3">
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">
        Companies hiring for this career
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {companies.map((company) => (
          <Link
            key={company.id}
            to={`/companies/${company.id}`}
            className="flex items-center gap-2.5 rounded-lg border border-border px-2.5 py-2 transition-colors hover:border-accent-soft/40"
          >
            <CompanyLogo company={company} size={28} />
            <span className="text-sm text-ink">{company.name}</span>
          </Link>
        ))}
      </div>
    </Surface>
  );
}
