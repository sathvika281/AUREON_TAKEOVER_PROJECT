import { EvidenceExplanation } from "../../design-system/components/EvidenceExplanation";
import { Surface } from "../../design-system/components/Surface";
import type { MentorMatch } from "../../shared/api/types";

export function MentorMatchCard({ match }: { match: MentorMatch }) {
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
        <span className="text-right text-xs text-ink-faint">
          Mentor: <span className="text-ink">{match.mentor_name}</span>
        </span>
      </div>
    </Surface>
  );
}
