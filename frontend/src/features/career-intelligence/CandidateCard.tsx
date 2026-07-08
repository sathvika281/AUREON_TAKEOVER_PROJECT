import { Link } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EvidenceExplanation } from "../../design-system/components/EvidenceExplanation";
import { Surface } from "../../design-system/components/Surface";
import type { CareerCandidate } from "../../shared/api/types";

/**
 * Same evidence-first ordering as HypothesisCard: Supporting -> Contradicting
 * -> Missing -> Evidence Strength (qualitative, never a raw number) ->
 * Uncertainty note -> the career name itself, last, as a working label
 * rather than a headline recommendation.
 */
export function CandidateCard({
  candidate,
  onShortlist,
  onRemove,
}: {
  candidate: CareerCandidate;
  onShortlist?: (careerId: string) => void;
  onRemove?: (careerId: string) => void;
}) {
  return (
    <Surface tone="raised" padding="md">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm leading-relaxed text-ink">{candidate.why_it_matches}</p>
        {candidate.is_shortlisted && <Badge tone="warm">Shortlisted</Badge>}
      </div>

      <EvidenceExplanation
        supporting={candidate.supporting_evidence}
        contradicting={candidate.contradicting_evidence}
        missing={candidate.missing_evidence}
      />

      {candidate.uncertainty_reason && (
        <p className="mt-3 rounded-lg bg-white/[0.03] px-3 py-2 text-xs italic leading-relaxed text-ink-muted">
          Why Aureon is still uncertain: {candidate.uncertainty_reason}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
        <span className="text-xs text-accent-soft">{candidate.evidence_strength}</span>
        <Link
          to={`/explore/career-reality/${candidate.career_id}`}
          className="text-right text-xs text-ink-faint transition hover:text-ink"
        >
          Candidate: <span className="text-ink">{candidate.career_name}</span>
        </Link>
      </div>

      {(onShortlist || onRemove) && (
        <div className="mt-3 flex gap-2">
          {onShortlist && !candidate.is_shortlisted && (
            <Button variant="ghost" size="md" onClick={() => onShortlist(candidate.career_id)}>
              Shortlist
            </Button>
          )}
          {onRemove && (
            <Button variant="ghost" size="md" onClick={() => onRemove(candidate.career_id)}>
              Remove
            </Button>
          )}
        </div>
      )}
    </Surface>
  );
}
