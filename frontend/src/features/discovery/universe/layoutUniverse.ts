import type { CareerHypothesis, CareerSummary, NotebookEntry, ReflectionEntry } from "../../../shared/api/types";

/**
 * Same discipline as ../network/layoutTraits.ts: pure functions mapping
 * real data to geometry, with zero randomness. A star's angle is a
 * stable hash of its id, so it never jumps between renders — only its
 * radius/size/opacity move, and only in response to real confidence
 * changes.
 */

export function hashToAngle(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  }
  return (hash % 360) * (Math.PI / 180);
}

// Progressive-disclosure thresholds on confidenceScore (0..1).
export const CLUSTER_THRESHOLD = 0.2;
export const LINES_THRESHOLD = 0.4;
export const LABEL_THRESHOLD = 0.7;

const STAR_FAR_RADIUS = 360;
const STAR_CLOSE_RADIUS = 230;
const STAR_MIN_SIZE = 6;
const STAR_MAX_SIZE = 14;
const STAR_MIN_OPACITY = 0.45;
const STAR_MAX_OPACITY = 1;

// A rejected hypothesis is never confidence-scaled — it's a fixed,
// deliberately near-invisible mark. Still real, still clickable, still
// honest about why Aureon moved away from it, just never mistaken for a
// live belief.
const REJECTED_STAR_SIZE = 5;
const REJECTED_STAR_OPACITY = 0.16;
const REJECTED_STAR_RADIUS = 400;

// How much a same-industry cluster pulls a star's angle toward the
// industry's shared angle as confidence rises through the cluster band —
// capped well below 1 so stars in the same industry never fully overlap.
const MAX_CLUSTER_PULL = 0.5;

/**
 * unexplored — no hypothesis exists for this career yet.
 * active — a real, live (non-discarded) hypothesis exists.
 * rejected — Aureon formed and then discarded a hypothesis here; kept
 * visible (barely) rather than erased, per "still available in history."
 */
export type StarState = "unexplored" | "active" | "rejected";

export interface UniverseStar {
  id: string;
  name: string;
  industry: string;
  oneLiner: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  state: StarState;
  /** Present whenever a real CareerHypothesis exists for this career,
   * active or rejected — this is what makes a star explainable. Null
   * only for genuinely unexplored careers. */
  hypothesis: CareerHypothesis | null;
}

function normalize(text: string): string {
  return text.trim().toLowerCase();
}

function findMatchingHypothesis(
  career: CareerSummary,
  hypotheses: CareerHypothesis[],
): CareerHypothesis | null {
  const target = normalize(career.name);
  return (
    hypotheses.find((h) => {
      const name = normalize(h.career_name);
      return name === target || name.includes(target) || target.includes(name);
    }) ?? null
  );
}

/**
 * The full open catalog, positioned as the "unexplored universe." Careers
 * with a matching live hypothesis move closer/brighter/larger in direct
 * proportion to that hypothesis's real confidence; everything else stays
 * at a fixed, equally-distant default — never fabricated distance.
 */
export function layoutCatalogStars(
  catalog: CareerSummary[],
  hypotheses: CareerHypothesis[],
  confidenceScore: number,
): UniverseStar[] {
  const clusterFactor =
    Math.max(0, Math.min(1, (confidenceScore - CLUSTER_THRESHOLD) / (LINES_THRESHOLD - CLUSTER_THRESHOLD))) *
    MAX_CLUSTER_PULL;

  return catalog.map((career) => {
    const hypothesis = findMatchingHypothesis(career, hypotheses);
    const isRejected = hypothesis?.status === "discarded";
    const state: StarState = hypothesis === null ? "unexplored" : isRejected ? "rejected" : "active";

    const baseAngle = hashToAngle(career.id);
    const industryAngle = hashToAngle(career.industry);
    const angle = baseAngle + (industryAngle - baseAngle) * clusterFactor;

    let radius: number;
    let size: number;
    let opacity: number;
    if (state === "rejected") {
      radius = REJECTED_STAR_RADIUS;
      size = REJECTED_STAR_SIZE;
      opacity = REJECTED_STAR_OPACITY;
    } else {
      const confidence = state === "active" ? hypothesis!.confidence : 0;
      radius = STAR_FAR_RADIUS - confidence * (STAR_FAR_RADIUS - STAR_CLOSE_RADIUS);
      size = STAR_MIN_SIZE + confidence * (STAR_MAX_SIZE - STAR_MIN_SIZE);
      opacity = STAR_MIN_OPACITY + confidence * (STAR_MAX_OPACITY - STAR_MIN_OPACITY);
    }

    return {
      id: career.id,
      name: career.name,
      industry: career.industry,
      oneLiner: career.one_liner,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      size,
      opacity,
      state,
      hypothesis,
    };
  });
}

export interface Constellation {
  industry: string;
  starIds: string[];
  centroid: { x: number; y: number };
  /** At least one real, live hypothesis lands in this industry. */
  isActive: boolean;
  showLines: boolean;
  showLabel: boolean;
  /** Which active-hypothesis stars are currently connected, strongest
   * confidence first — grows from 2 toward every active member as
   * confidenceScore rises, so the constellation completes itself the
   * same way the student's real understanding does: gradually, and only
   * ever between careers Aureon actually has evidence for. */
  connectedStarIds: string[];
}

/**
 * Groups the same real `industry` field the catalog already carries.
 * Lines/labels are gated behind confidenceScore, not revealed all at
 * once — discovery should feel earned.
 */
export function layoutConstellations(stars: UniverseStar[], confidenceScore: number): Constellation[] {
  const byIndustry = new Map<string, UniverseStar[]>();
  for (const star of stars) {
    const group = byIndustry.get(star.industry) ?? [];
    group.push(star);
    byIndustry.set(star.industry, group);
  }

  return Array.from(byIndustry.entries())
    .filter(([, group]) => group.length >= 2)
    .map(([industry, group]) => {
      const activeMembers = group
        .filter((s) => s.state === "active")
        .sort((a, b) => (b.hypothesis?.confidence ?? 0) - (a.hypothesis?.confidence ?? 0));
      const isActive = activeMembers.length > 0;
      const centroid = {
        x: group.reduce((sum, s) => sum + s.x, 0) / group.length,
        y: group.reduce((sum, s) => sum + s.y, 0) / group.length,
      };

      const revealProgress = Math.max(
        0,
        Math.min(1, (confidenceScore - LINES_THRESHOLD) / (1 - LINES_THRESHOLD)),
      );
      const revealedCount =
        activeMembers.length < 2 ? 0 : Math.round(2 + revealProgress * (activeMembers.length - 2));

      return {
        industry,
        starIds: group.map((s) => s.id),
        centroid,
        isActive,
        showLines: isActive && confidenceScore >= LINES_THRESHOLD,
        showLabel: isActive && confidenceScore >= LABEL_THRESHOLD,
        connectedStarIds: activeMembers.slice(0, revealedCount).map((s) => s.id),
      };
    });
}

export interface EvidenceOrbit {
  key: string;
  label: string;
  count: number;
  radius: number;
  latestText: string | null;
}

export interface DecorativeStar {
  x: number;
  y: number;
  r: number;
  opacity: number;
}

const DECORATIVE_STAR_COUNT = 70;

/** Deterministic, non-random background texture — the "infinite
 * universe" illusion, shared by CareerUniverse and CinematicOpen. Purely
 * decorative: no click handler, no label, no data behind it. */
export function decorativeStars(): DecorativeStar[] {
  return Array.from({ length: DECORATIVE_STAR_COUNT }, (_, i) => {
    const angle = ((i * 137.508) % 360) * (Math.PI / 180);
    const radius = 40 + ((i * 53) % 470);
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      r: 0.5 + (i % 3) * 0.35,
      opacity: 0.12 + (i % 5) * 0.04,
    };
  });
}

export interface StarfieldLayer {
  depth: number;
  driftSeconds: number;
  stars: DecorativeStar[];
}

const LAYER_CONFIG = [
  { count: 140, minRadius: 60, maxRadius: 900, minR: 0.35, maxR: 0.8, minOpacity: 0.08, maxOpacity: 0.16, driftSeconds: 220 },
  { count: 80, minRadius: 200, maxRadius: 850, minR: 0.7, maxR: 1.3, minOpacity: 0.14, maxOpacity: 0.26, driftSeconds: 150 },
  { count: 40, minRadius: 300, maxRadius: 800, minR: 1.1, maxR: 1.9, minOpacity: 0.2, maxOpacity: 0.4, driftSeconds: 95 },
] as const;

/**
 * "Thousands of tiny stars" without ever feeling like wallpaper: three
 * deterministic depth bands (same golden-angle lattice as
 * decorativeStars, zero randomness), each drifting at its own very slow,
 * fixed, infinite rotation speed — nearer bands move slightly faster,
 * giving real parallax depth. Purely ambient: this is the one place
 * continuous idle motion is allowed, since it represents the universe
 * existing, not a claim about the student (see the redesign's governing
 * motion rule).
 */
export function layeredStarfield(): StarfieldLayer[] {
  return LAYER_CONFIG.map((layer, layerIndex) => ({
    depth: layerIndex,
    driftSeconds: layer.driftSeconds,
    stars: Array.from({ length: layer.count }, (_, i) => {
      const seed = layerIndex * 1000 + i;
      const angle = ((seed * 137.508) % 360) * (Math.PI / 180);
      const radius = layer.minRadius + ((seed * 71) % (layer.maxRadius - layer.minRadius));
      const rJitter = (seed % 7) / 7;
      const opJitter = (seed % 11) / 11;
      return {
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        r: layer.minR + rJitter * (layer.maxR - layer.minR),
        opacity: layer.minOpacity + opJitter * (layer.maxOpacity - layer.minOpacity),
      };
    }),
  }));
}

const VISIBLE_UNEXPLORED_BASE = 6;
const NOTEBOOK_ENTRIES_PER_REVEALED_STAR = 2;

/**
 * "Most of the screen should remain empty" made concrete: every real
 * active/rejected star (evidence-backed, never hidden) always renders,
 * but genuinely unexplored careers only reveal a small, deterministic,
 * slowly-growing slice of the full catalog — never the whole catalog at
 * once. The slice grows with real notebookEntries.length, so "the
 * visible universe expands" is a direct, honest reaction to real
 * evidence accumulating, not a timer or a random reveal. Selection order
 * is stable (by id) so the same stars persist across renders.
 */
export function selectVisibleStars(stars: UniverseStar[], notebookEntryCount: number): UniverseStar[] {
  const evidenced = stars.filter((s) => s.state !== "unexplored");
  const unexplored = stars
    .filter((s) => s.state === "unexplored")
    .slice()
    .sort((a, b) => a.id.localeCompare(b.id));

  const revealCount = Math.min(
    unexplored.length,
    VISIBLE_UNEXPLORED_BASE + Math.floor(notebookEntryCount / NOTEBOOK_ENTRIES_PER_REVEALED_STAR),
  );

  return [...evidenced, ...unexplored.slice(0, revealCount)];
}

const ORBIT_START_RADIUS = 380;
const ORBIT_STEP = 18;
const MAX_ORBITS = 6;

function titleCase(text: string): string {
  return text.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * One ring per real, distinct Discovery Notebook `source` value, plus a
 * dedicated Reflection Journal ring — every ring's thickness/label comes
 * directly from real entry counts, never a placeholder.
 */
export function layoutEvidenceOrbits(
  notebookEntries: NotebookEntry[],
  reflectionJournal: ReflectionEntry[],
): EvidenceOrbit[] {
  const bySource = new Map<string, NotebookEntry[]>();
  for (const entry of notebookEntries) {
    const group = bySource.get(entry.source) ?? [];
    group.push(entry);
    bySource.set(entry.source, group);
  }

  const orbits: EvidenceOrbit[] = Array.from(bySource.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([source, entries]) => ({
      key: source,
      label: titleCase(source),
      count: entries.length,
      radius: 0,
      latestText:
        [...entries].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]
          ?.text ?? null,
    }));

  if (reflectionJournal.length > 0) {
    const answered = reflectionJournal.filter((r) => r.response);
    orbits.push({
      key: "reflection_journal",
      label: "Reflection Journal",
      count: answered.length,
      radius: 0,
      latestText: [...answered].sort(
        (a, b) => new Date(b.answered_at ?? 0).getTime() - new Date(a.answered_at ?? 0).getTime(),
      )[0]?.response ?? null,
    });
  }

  return orbits.slice(0, MAX_ORBITS).map((orbit, index) => ({
    ...orbit,
    radius: ORBIT_START_RADIUS + index * ORBIT_STEP,
  }));
}
