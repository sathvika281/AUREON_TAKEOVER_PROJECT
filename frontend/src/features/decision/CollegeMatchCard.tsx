import { useState } from "react";

import { EvidenceExplanation } from "../../design-system/components/EvidenceExplanation";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { CollegeMatch, InstitutionDetail } from "../../shared/api/types";

/** A visitable world, not a text badge — brightness (the ring's opacity
 * and its lit center) carries the same real evidence-strength enum the
 * backend returns for mentors. */
const STRENGTH_STYLE: Record<CollegeMatch["evidence_strength"], { size: number; opacity: number }> = {
  Strong: { size: 5, opacity: 1 },
  Growing: { size: 4, opacity: 0.7 },
  "Needs More Evidence": { size: 3, opacity: 0.4 },
};

function NearbyWorld({ strength }: { strength: CollegeMatch["evidence_strength"] }) {
  const s = STRENGTH_STYLE[strength];
  return (
    <span className="relative inline-flex h-3 w-3 shrink-0 items-center justify-center" aria-hidden="true">
      <span
        className="absolute inset-0 rounded-full border"
        style={{ borderColor: `rgba(127,176,150,${s.opacity})` }}
      />
      <span
        className="rounded-full bg-accent-soft"
        style={{ width: s.size, height: s.size, opacity: s.opacity }}
      />
    </span>
  );
}

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
        <p className="mt-3 border-l border-border-strong pl-3 text-xs italic leading-relaxed text-ink-muted">
          Why Aureon is still uncertain: {match.uncertainty_reason}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
        <span className="flex items-center gap-2 text-xs text-accent-soft">
          <NearbyWorld strength={match.evidence_strength} />
          {match.evidence_strength}
        </span>
        <button onClick={toggle} className="text-right text-xs text-ink-faint transition-colors hover:text-ink">
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
