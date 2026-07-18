import type { CareerHypothesis, EvidenceRecord, ReflectionEntry } from "../../../shared/api/types";
import type { TraitNodeLayout } from "../network/layoutTraits";
import type { UniverseStar } from "./layoutUniverse";

/**
 * Same discipline as layoutUniverse.ts: pure functions, real data only,
 * zero fabrication. Every explanation here reads fields that already
 * exist on the student's real profile — nothing here invents a new
 * evidence system, a new score, or a new percentage. Reused everywhere a
 * hover/tap tooltip needs to answer "why is this part of my universe."
 */

export interface UniverseExplanation {
  title: string;
  subtitle?: string;
  why: string[];
  /** e.g. "2 conversation notes · 1 experiment" — null when there's
   * nothing real to cite. */
  evidenceLine: string | null;
  isLowEvidence: boolean;
}

export const LOW_EVIDENCE_FALLBACK =
  "This connection is still emerging. Explore and reflect more to help Aureon understand whether this path belongs in your universe.";

// Mirrors agents/specialized/career_intelligence/confidence.py's exact
// thresholds/vocabulary — the established "confidence -> qualitative
// label, never a raw number" convention, not a new one.
const STRONG_THRESHOLD = 0.6;
const GROWING_THRESHOLD = 0.3;

export type EvidenceTier = "Strong" | "Growing" | "Needs More Evidence";

export function tierForScore(score: number | null): EvidenceTier {
  const s = score ?? 0;
  if (s >= STRONG_THRESHOLD) return "Strong";
  if (s >= GROWING_THRESHOLD) return "Growing";
  return "Needs More Evidence";
}

export function titleCase(text: string): string {
  return text.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function normalize(text: string): string {
  return text.trim().toLowerCase();
}

/** Same fuzzy matching StarExplainPanel/layoutUniverse already use for
 * relating a catalog career to notebook/evidence entries — never a guess,
 * only ever a real backend-tagged related_career/related_hypothesis. */
function evidenceForStar(star: UniverseStar, evidenceGraph: EvidenceRecord[]): EvidenceRecord[] {
  const target = normalize(star.name);
  const matches = (value: string | null) => {
    if (!value) return false;
    const name = normalize(value);
    return name === target || name.includes(target) || target.includes(name);
  };
  return evidenceGraph.filter((e) => e.related_career === star.id || matches(e.related_hypothesis));
}

function summarizeBySource(records: EvidenceRecord[]): string | null {
  if (records.length === 0) return null;
  const counts = new Map<string, number>();
  for (const record of records) {
    counts.set(record.source, (counts.get(record.source) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([source, count]) => `${count} ${titleCase(source)}${count === 1 ? "" : "s"}`)
    .join(" · ");
}

export function explainStar(star: UniverseStar, evidenceGraph: EvidenceRecord[]): UniverseExplanation {
  const hypothesis = star.hypothesis;
  if (!hypothesis) {
    return {
      title: star.name,
      subtitle: titleCase(star.industry),
      why: [star.oneLiner],
      evidenceLine: null,
      isLowEvidence: true,
    };
  }

  const related = evidenceForStar(star, evidenceGraph);
  const why = hypothesis.supporting_evidence.slice(0, 2);
  const evidenceLine = summarizeBySource(related);

  return {
    title: star.name,
    subtitle: titleCase(star.industry),
    why: why.length > 0 ? why : [hypothesis.transition_reason || star.oneLiner],
    evidenceLine,
    isLowEvidence: why.length === 0 && !evidenceLine,
  };
}

export function explainConstellationLine(
  starA: UniverseStar,
  starB: UniverseStar,
  industry: string,
): UniverseExplanation {
  const why = [`Both are in the ${titleCase(industry)} field.`];

  const evidenceA = starA.hypothesis?.supporting_evidence.length ?? 0;
  const evidenceB = starB.hypothesis?.supporting_evidence.length ?? 0;
  let evidenceLine: string | null = null;
  if (evidenceA > 0 || evidenceB > 0) {
    why.push("You've been exploring both independently:");
    evidenceLine = `${starA.name} (${evidenceA}) · ${starB.name} (${evidenceB})`;
  }

  return {
    title: `${starA.name} ↔ ${starB.name}`,
    subtitle: titleCase(industry),
    why,
    evidenceLine,
    isLowEvidence: evidenceA === 0 && evidenceB === 0,
  };
}

export function explainTrait(trait: TraitNodeLayout, evidenceGraph: EvidenceRecord[]): UniverseExplanation {
  const related = evidenceGraph.filter((e) => e.related_trait === trait.name);
  const tier = tierForScore(trait.score);
  return {
    title: trait.label,
    subtitle: tier,
    why: trait.summary ? [trait.summary] : [],
    evidenceLine: summarizeBySource(related),
    isLowEvidence: trait.score === null && related.length === 0,
  };
}

export interface MoonSummary {
  worldsExplored: number;
  evidenceCollected: number;
  experimentsEngaged: number;
  reflectionsAnswered: number;
}

export function explainMoon(
  hypotheses: CareerHypothesis[],
  evidenceGraph: EvidenceRecord[],
  reflectionJournal: ReflectionEntry[],
): MoonSummary {
  return {
    worldsExplored: hypotheses.filter((h) => h.status !== "discarded").length,
    evidenceCollected: evidenceGraph.length,
    experimentsEngaged: evidenceGraph.filter((e) => e.source === "experiment").length,
    reflectionsAnswered: reflectionJournal.filter((r) => r.response).length,
  };
}

export function explainMoonTooltip(summary: MoonSummary): UniverseExplanation {
  const hasAnything =
    summary.worldsExplored > 0 ||
    summary.evidenceCollected > 0 ||
    summary.experimentsEngaged > 0 ||
    summary.reflectionsAnswered > 0;

  return {
    title: "Your Universe",
    why: [
      "This is your evolving career universe — shaped by what you've explored, reflected on, and tried.",
    ],
    evidenceLine: hasAnything
      ? `${summary.worldsExplored} worlds explored · ${summary.evidenceCollected} evidence collected · ${summary.experimentsEngaged} experiments · ${summary.reflectionsAnswered} reflections`
      : null,
    isLowEvidence: !hasAnything,
  };
}
