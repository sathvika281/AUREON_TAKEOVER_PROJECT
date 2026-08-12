import { useCallback, useEffect, useRef, useState } from "react";
import { Handshake, ShieldAlert } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { PageHeader } from "../../design-system/components/PageHeader";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { OpportunityEqualityRecommendation, OpportunityEqualityResponse } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";
import { useSuggestionsContext } from "../suggestions/SuggestionsContext";

const LIKELIHOOD_TONE: Record<string, "warm" | "cool" | "neutral"> = {
  low: "warm",
  medium: "cool",
  high: "neutral",
};

const LIKELIHOOD_LABEL: Record<string, string> = {
  low: "Easy to Miss",
  medium: "Somewhat Findable",
  high: "Well-Known",
};

const CATEGORY_LABELS: Record<string, string> = {
  internship: "Internship",
  hackathon: "Hackathon",
  research_program: "Research Program",
  competition: "Competition",
  scholarship: "Scholarship",
  open_source_program: "Open Source Program",
  fellowship: "Fellowship",
  campus_ambassador_program: "Campus Ambassador Program",
  conference: "Conference",
  workshop: "Workshop",
  bootcamp: "Bootcamp",
  innovation_challenge: "Innovation Challenge",
  // Explore Polish Batch additions.
  government_scheme: "Government Scheme",
  mentorship_program: "Mentorship Program",
  certification: "Certification",
  funding_grant: "Funding / Grant",
  community_program: "Community Program",
};

/**
 * Opportunity Equality — "these are opportunities you are least likely
 * to discover on your own," never "here are today's opportunities."
 * Every card visibly shows its real why-shown sentence.
 */
export function OpportunityEqualityScreen() {
  const studentId = useRef(getCurrentStudentId()).current;
  const [recommendations, setRecommendations] = useState<OpportunityEqualityRecommendation[]>([]);
  // Loading, a genuine fetch failure, and genuinely nothing surfaced yet
  // are three different product states.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const { openModal } = useSuggestionsContext();

  const loadRecommendations = useCallback(() => {
    setStatus("loading");
    apiClient
      .get<OpportunityEqualityResponse>(`/v1/students/${studentId}/opportunity-equality`)
      .then((r) => {
        setRecommendations(r.recommendations);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [studentId]);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const save = (opportunityId: string) => {
    setSavedIds((prev) => new Set(prev).add(opportunityId));
    void apiClient.post(`/v1/students/${studentId}/opportunity-equality/interact`, {
      opportunity_id: opportunityId,
      interaction: "saved",
    });
  };

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <PageHeader
        title="Opportunity Equality"
        description="Opportunities you're least likely to discover on your own — never just today's listings."
      />

      {status === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : status === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Opportunities"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
            action={<Button variant="secondary" onClick={loadRecommendations}>Retry</Button>}
          />
        </div>
      ) : recommendations.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Handshake}
            title="Nothing Surfaced Yet"
            description="Aureon needs a bit more real signal about you (from Discover) before it can find opportunities you might otherwise miss."
          />
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {recommendations.map((rec) => (
            <Surface key={rec.opportunity.id} tone="raised" padding="lg">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-ink">{rec.opportunity.title}</p>
                  <p className="mt-1 text-xs text-ink-faint">{rec.opportunity.organization}</p>
                  <Badge tone="cool" className="mt-1.5">
                    {CATEGORY_LABELS[rec.opportunity.category] ?? rec.opportunity.category}
                  </Badge>
                </div>
                <Badge tone={LIKELIHOOD_TONE[rec.likelihood_of_self_discovery]}>
                  {LIKELIHOOD_LABEL[rec.likelihood_of_self_discovery]}
                </Badge>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-ink-muted">{rec.opportunity.description}</p>
              <p className="mt-3 text-sm leading-relaxed text-ink">{rec.why_shown}</p>
              {rec.contributing_factors.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {rec.contributing_factors.map((f) => (
                    <li key={f} className="text-xs text-ink-faint">• {f}</li>
                  ))}
                </ul>
              )}
              <div className="mt-4 flex items-center gap-4">
                {/* Sprint 4 — an illustrative composite posting has no real
                 * destination to link to; showing nothing is more honest
                 * than a link that goes nowhere. */}
                {rec.opportunity.official_link && (
                  <a
                    href={rec.opportunity.official_link}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-medium text-accent-soft transition-colors hover:text-accent"
                  >
                    View Details
                  </a>
                )}
                <button
                  onClick={() => save(rec.opportunity.id)}
                  disabled={savedIds.has(rec.opportunity.id)}
                  className="text-xs text-ink-faint transition-colors hover:text-ink-muted disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {savedIds.has(rec.opportunity.id) ? "Saved" : "Save"}
                </button>
                <button
                  onClick={() =>
                    openModal({
                      category: "correction",
                      context_type: "opportunity",
                      context_id: rec.opportunity.id,
                      context_metadata: {
                        page_or_feature: "Opportunity Equality",
                        opportunity_title: rec.opportunity.title,
                      },
                    })
                  }
                  className="text-xs text-ink-faint transition-colors hover:text-ink-muted"
                >
                  Report an issue
                </button>
              </div>
            </Surface>
          ))}
        </div>
      )}
    </div>
  );
}
