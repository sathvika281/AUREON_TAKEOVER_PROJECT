import { motion } from "framer-motion";
import { ArrowRight, X } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "../../../design-system/components/Badge";
import { EvidenceExplanation } from "../../../design-system/components/EvidenceExplanation";
import { EASE_CALM } from "../../../design-system/motion";
import type { NotebookEntry } from "../../../shared/api/types";
import { BeliefRevisionEntry } from "../notebook/BeliefRevisionEntry";
import type { UniverseStar } from "./layoutUniverse";

const STATUS_LABEL: Record<string, string> = {
  investigating: "Investigating",
  growing: "Growing",
  strong: "Strong Signal",
  validated: "Validated",
  discarded: "Rejected",
};

function titleCase(text: string): string {
  return text.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Real belief-revision notebook entries recorded against this exact
 * career — the same fuzzy match layoutUniverse already uses to connect a
 * catalog career to its live hypothesis, applied here to the notebook's
 * own `related_career`/`related_hypothesis` fields. Never a guess: an
 * entry only counts if the backend actually tagged it to this career. */
function timelineFor(entries: NotebookEntry[], careerName: string): NotebookEntry[] {
  const target = careerName.trim().toLowerCase();
  const matches = (value: string | null) => {
    if (!value) return false;
    const name = value.trim().toLowerCase();
    return name === target || name.includes(target) || target.includes(name);
  };
  return entries
    .filter((e) => e.kind === "belief_revision" && (matches(e.related_career) || matches(e.related_hypothesis)))
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
}

/**
 * An astronomical observation, not a settings modal — no uniform bordered
 * box, a soft glow-edged field-note read directly off real
 * CareerHypothesis fields plus the real belief-revision trail in the
 * Discovery Notebook. A catalog star with no matching hypothesis yet
 * gets an equally honest state: its real one-liner, and a plain
 * statement that no evidence connects it to this student yet. Rejected
 * hypotheses stay fully explainable too — Aureon's reasoning for moving
 * away from a career is exactly as real as its reasoning for moving
 * toward one, and is never hidden.
 */
export function StarExplainPanel({
  star,
  notebookEntries,
  onClose,
}: {
  star: UniverseStar;
  notebookEntries: NotebookEntry[];
  onClose: () => void;
}) {
  const hypothesis = star.hypothesis;
  const timeline = hypothesis ? timelineFor(notebookEntries, star.name) : [];

  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 24 }}
      transition={{ duration: 0.6, ease: EASE_CALM }}
      className="absolute right-6 top-6 z-20 max-h-[calc(100%-3rem)] w-80 overflow-y-auto rounded-3xl border border-[#2A2650]/70 bg-[#0C0A22]/85 p-5 shadow-[0_24px_60px_rgba(0,0,0,0.55)] backdrop-blur-md"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-serif text-lg text-[#F2EDE0]">{star.name}</p>
          <p className="mt-0.5 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-[#6E6A5E]">
            {titleCase(star.industry)}
          </p>
        </div>
        <button onClick={onClose} className="shrink-0 text-[#6E6A5E] transition-colors hover:text-[#F2EDE0]">
          <X size={15} />
        </button>
      </div>

      {hypothesis ? (
        <>
          <div className="mt-4 flex items-center justify-between border-y border-[#2A2650]/70 py-3">
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#6E6A5E]">Confidence</p>
              <p className="mt-1 text-2xl font-light text-[#F2EDE0]">
                {Math.round(hypothesis.confidence * 100)}%
              </p>
            </div>
            <div className="text-right">
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#6E6A5E]">
                Current Status
              </p>
              <div className="mt-1.5">
                <Badge tone={star.state === "rejected" ? "cool" : "gold"}>
                  {STATUS_LABEL[hypothesis.status] ?? titleCase(hypothesis.status)}
                </Badge>
              </div>
            </div>
          </div>

          {star.state === "rejected" && (
            <p className="mt-3 text-xs italic leading-relaxed text-[#6E6A5E]">
              Aureon considered this direction and moved away from it. Kept here, dim, for full
              transparency — nothing about a student's journey is erased.
            </p>
          )}

          {hypothesis.transition_reason && (
            <div className="mt-3">
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#6E6A5E]">
                Why Aureon Believes This
              </p>
              <p className="mt-1.5 text-xs leading-relaxed text-[#9C978A]">{hypothesis.transition_reason}</p>
            </div>
          )}

          <div className="mt-3">
            <EvidenceExplanation
              supporting={hypothesis.supporting_evidence}
              contradicting={hypothesis.contradicting_evidence}
              missing={hypothesis.missing_evidence}
              markerClassName="text-[#D9B87A]"
            />
          </div>

          <div className="mt-4 border-t border-[#2A2650]/70 pt-3">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#6E6A5E]">
              Timeline
            </p>
            {timeline.length > 0 ? (
              <div className="mt-1">
                {timeline.map((entry) => (
                  <BeliefRevisionEntry key={entry.id} entry={entry} />
                ))}
              </div>
            ) : (
              <p className="mt-1.5 text-xs italic leading-relaxed text-[#6E6A5E]">
                No timeline yet — this understanding hasn't changed since it first appeared.
              </p>
            )}
          </div>

          <Link
            to={`/explore/career-reality/${star.id}`}
            className="mt-4 flex items-center gap-1.5 text-xs text-[#D9B87A] transition-opacity hover:opacity-80"
          >
            Explore this world <ArrowRight size={13} />
          </Link>
        </>
      ) : (
        <>
          <p className="mt-3 text-xs leading-relaxed text-[#9C978A]">{star.oneLiner}</p>
          <p className="mt-3 border-l border-[#3A3560] pl-3 text-[0.7rem] italic leading-relaxed text-[#6E6A5E]">
            No supporting evidence has been collected yet — every conversation could change that.
          </p>
        </>
      )}
    </motion.div>
  );
}
