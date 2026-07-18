import { EvidenceExplanation } from "../../design-system/components/EvidenceExplanation";
import { Surface } from "../../design-system/components/Surface";
import type { MentorMatch } from "../../shared/api/types";

/** Brightness carries real evidence strength — never decorative. The
 * same three-value enum the backend returns, rendered as a star's actual
 * brightness rather than a text label alone. */
const STRENGTH_STYLE: Record<MentorMatch["evidence_strength"], { size: number; opacity: number; glow: number }> = {
  Strong: { size: 8, opacity: 1, glow: 9 },
  Growing: { size: 6, opacity: 0.72, glow: 4 },
  "Needs More Evidence": { size: 4, opacity: 0.4, glow: 0 },
};

function GuidingStar({ strength }: { strength: MentorMatch["evidence_strength"] }) {
  const s = STRENGTH_STYLE[strength];
  return (
    <span
      className="inline-block shrink-0 rounded-full bg-accent-soft"
      style={{
        width: s.size,
        height: s.size,
        opacity: s.opacity,
        boxShadow: s.glow ? `0 0 ${s.glow}px rgba(127,176,150,0.7)` : undefined,
      }}
      aria-hidden="true"
    />
  );
}

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
        <p className="mt-3 border-l border-border-strong pl-3 text-xs italic leading-relaxed text-ink-muted">
          Why Aureon is still uncertain: {match.uncertainty_reason}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
        <span className="flex items-center gap-2 text-xs text-accent-soft">
          <GuidingStar strength={match.evidence_strength} />
          {match.evidence_strength}
        </span>
        <span className="text-right text-xs text-ink-faint">
          Mentor: <span className="text-ink">{match.mentor_name}</span>
        </span>
      </div>
    </Surface>
  );
}
