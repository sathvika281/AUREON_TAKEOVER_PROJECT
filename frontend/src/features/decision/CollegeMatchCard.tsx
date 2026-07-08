import { useState } from "react";

import { EvidenceExplanation } from "../../design-system/components/EvidenceExplanation";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { CollegeMatch, InstitutionDetail } from "../../shared/api/types";

export function CollegeMatchCard({ match }: { match: CollegeMatch }) {
  const [detail, setDetail] = useState<InstitutionDetail | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const toggle = () => {
    setIsExpanded((prev) => !prev);
    if (!detail && !isExpanded) {
      setIsLoading(true);
      apiClient
        .get<InstitutionDetail>(`/v1/institutions/${match.institution_id}`)
        .then(setDetail)
        .catch(() => {})
        .finally(() => setIsLoading(false));
    }
  };

  return (
    <Surface tone="raised" padding="md">
      <p className="text-sm leading-relaxed text-ink">{match.why_it_matches}</p>

      <EvidenceExplanation
        supporting={match.supporting_evidence}
        contradicting={match.contradicting_evidence}
        missing={match.missing_evidence}
      />

      {match.uncertainty_reason && (
        <p className="mt-3 rounded-lg bg-white/[0.03] px-3 py-2 text-xs italic leading-relaxed text-ink-muted">
          Why Aureon is still uncertain: {match.uncertainty_reason}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
        <span className="text-xs text-accent-soft">{match.evidence_strength}</span>
        <button onClick={toggle} className="text-right text-xs text-ink-faint transition hover:text-ink">
          Institution: <span className="text-ink">{match.institution_name}</span>
        </button>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-2 border-t border-border pt-3 text-xs leading-relaxed text-ink-muted">
          {isLoading && <p className="text-ink-faint">Loading…</p>}
          {detail && (
            <>
              <p><span className="text-ink-faint">Location: </span>{detail.city}, {detail.country}</p>
              <p><span className="text-ink-faint">Research culture: </span>{detail.research_culture}</p>
              <p><span className="text-ink-faint">Innovation ecosystem: </span>{detail.innovation_ecosystem}</p>
              <p><span className="text-ink-faint">Industry collaboration: </span>{detail.industry_collaboration}</p>
              <p><span className="text-ink-faint">Placements: </span>{detail.placements}</p>
              {detail.research_labs.length > 0 && (
                <p><span className="text-ink-faint">Research labs: </span>{detail.research_labs.map((l) => l.name).join(", ")}</p>
              )}
              {detail.student_organizations.length > 0 && (
                <p><span className="text-ink-faint">Student organizations: </span>{detail.student_organizations.map((o) => o.name).join(", ")}</p>
              )}
              {detail.academic_programs.length > 0 && (
                <p><span className="text-ink-faint">Academic programs: </span>{detail.academic_programs.map((p) => p.name).join(", ")}</p>
              )}
            </>
          )}
        </div>
      )}
    </Surface>
  );
}
