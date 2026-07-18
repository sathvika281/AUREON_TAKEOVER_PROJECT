import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { apiClient } from "../../../shared/api/client";
import type {
  CareerHypothesis,
  CareerSummary,
  EvidenceRecord,
  HiddenPotentialPattern,
  NotebookEntry,
  ReflectionEntry,
  TraitSignal,
} from "../../../shared/api/types";
import { DURATION, EASE_CALM } from "../../../design-system/motion";
import { getCurrentStudentId } from "../../../shared/config/studentId";
import { InsightMoment } from "../reveal/InsightMoment";
import { CinematicOpen } from "./CinematicOpen";
import { CurrentUnderstandingPanel } from "./CurrentUnderstandingPanel";
import { DiscoveryMilestoneRail } from "./DiscoveryMilestoneRail";
import { titleCase } from "./explainUniverse";
import {
  layeredStarfield,
  layoutCatalogStars,
  layoutConstellations,
  layoutEvidenceOrbits,
  selectVisibleStars,
  type UniverseStar,
} from "./layoutUniverse";
import { ConstellationLines } from "./ConstellationLines";
import { EvidenceOrbitRing } from "./EvidenceOrbitRing";
import { LiveStatusBar } from "./LiveStatusBar";
import { MoonCore } from "./MoonCore";
import { NebulaCloud } from "./NebulaCloud";
import { Star } from "./Star";
import { StarExplainPanel } from "./StarExplainPanel";

const SCENE_SIZE = 1000;
const CAMERA_ZOOM = 1.2;
const WOW_CAMERA_SCALE = 0.9;
const SEQUENCE_DURATION_MS = 2500;
const CINEMATIC_OPEN_SEEN_PREFIX = "aureon.seen_cinematic_open.";
const NARROW_BREAKPOINT = 768;

/** The one explicit responsive rule: below `NARROW_BREAKPOINT`, the
 * Moon's asymmetrical off-center placement collapses toward the true
 * center so floating panels have room to stack instead of overlapping. */
function useIsNarrowViewport(): boolean {
  const [isNarrow, setIsNarrow] = useState(
    () => typeof window !== "undefined" && window.innerWidth < NARROW_BREAKPOINT,
  );
  useEffect(() => {
    const onResize = () => setIsNarrow(window.innerWidth < NARROW_BREAKPOINT);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return isNarrow;
}

export function CareerUniverse({
  careerDna,
  hypotheses,
  notebookEntries,
  hiddenPotential,
  evidenceGraph,
  reflectionJournal,
  confidenceScore,
  understandingStage,
  understandingNarrative,
  isThinking,
  insightMomentLine,
  onDismissInsightMoment,
}: {
  careerDna: Record<string, TraitSignal>;
  hypotheses: CareerHypothesis[];
  notebookEntries: NotebookEntry[];
  hiddenPotential: HiddenPotentialPattern[];
  evidenceGraph: EvidenceRecord[];
  reflectionJournal: ReflectionEntry[];
  confidenceScore: number;
  understandingStage: string;
  understandingNarrative: string;
  isThinking: boolean;
  insightMomentLine: string | null;
  onDismissInsightMoment: () => void;
}) {
  const [catalog, setCatalog] = useState<CareerSummary[]>([]);
  const [selectedStar, setSelectedStar] = useState<UniverseStar | null>(null);
  const [sequenceActive, setSequenceActive] = useState(false);
  const [highlightedStarIds, setHighlightedStarIds] = useState<Set<string>>(new Set());
  const [dismissToken, setDismissToken] = useState(0);
  const previousSignatureRef = useRef<string | null>(null);
  const isNarrow = useIsNarrowViewport();

  const handleHoverLine = useCallback((ids: [string, string] | null) => {
    setHighlightedStarIds(ids ? new Set(ids) : new Set());
  }, []);

  const dismissAll = useCallback(() => {
    setSelectedStar(null);
    setDismissToken((t) => t + 1);
  }, []);

  const studentId = useRef(getCurrentStudentId()).current;
  const cinematicSeenKey = `${CINEMATIC_OPEN_SEEN_PREFIX}${studentId}`;
  const [showCinematic, setShowCinematic] = useState(
    () => notebookEntries.length === 0 && hypotheses.length === 0 && !localStorage.getItem(cinematicSeenKey),
  );

  useEffect(() => {
    apiClient
      .get<CareerSummary[]>("/v1/careers")
      .then(setCatalog)
      .catch(() => setCatalog([]));
  }, []);

  // Calm discovery sequence — fires only when real evidence actually
  // changed since last render, never on every render.
  useEffect(() => {
    const signature = `${notebookEntries.length}|${hypotheses.map((h) => h.confidence.toFixed(2)).join(",")}`;
    if (previousSignatureRef.current !== null && previousSignatureRef.current !== signature) {
      setSequenceActive(true);
      const timer = setTimeout(() => setSequenceActive(false), SEQUENCE_DURATION_MS);
      previousSignatureRef.current = signature;
      return () => clearTimeout(timer);
    }
    previousSignatureRef.current = signature;
  }, [notebookEntries.length, hypotheses]);

  const stars = useMemo(
    () => layoutCatalogStars(catalog, hypotheses, confidenceScore),
    [catalog, hypotheses, confidenceScore],
  );
  const visibleStars = useMemo(
    () => selectVisibleStars(stars, notebookEntries.length),
    [stars, notebookEntries.length],
  );
  const constellations = useMemo(
    () => layoutConstellations(visibleStars, confidenceScore),
    [visibleStars, confidenceScore],
  );
  const orbits = useMemo(
    () => layoutEvidenceOrbits(notebookEntries, reflectionJournal),
    [notebookEntries, reflectionJournal],
  );
  const starfield = useMemo(() => layeredStarfield(), []);

  // Real industry-constellation membership per star, only once that
  // constellation's lines are actually shown — feeds each Star's hover
  // tooltip so hovering the star itself also surfaces the relationship,
  // without needing pixel-precise line targeting.
  const starConstellationLabel = useMemo(() => {
    const map = new Map<string, string>();
    for (const constellation of constellations) {
      if (!constellation.showLines) continue;
      for (const id of constellation.connectedStarIds) {
        map.set(id, titleCase(constellation.industry));
      }
    }
    return map;
  }, [constellations]);

  const wowActive = insightMomentLine !== null;
  const originX = isNarrow ? SCENE_SIZE / 2 : SCENE_SIZE * 0.4;
  const originY = isNarrow ? SCENE_SIZE / 2 : SCENE_SIZE * 0.46;

  const cameraX = selectedStar ? selectedStar.x * (1 - CAMERA_ZOOM) : 0;
  const cameraY = selectedStar ? selectedStar.y * (1 - CAMERA_ZOOM) : 0;
  const cameraScale = selectedStar ? CAMERA_ZOOM : wowActive ? WOW_CAMERA_SCALE : 1;

  return (
    <div className="relative h-full min-h-[640px] w-full overflow-hidden bg-[#070B18]">
      {showCinematic && (
        <CinematicOpen
          onComplete={() => {
            localStorage.setItem(cinematicSeenKey, "true");
            setShowCinematic(false);
          }}
        />
      )}

      <motion.div
        className="pointer-events-none absolute inset-0 bg-black"
        animate={{ opacity: sequenceActive ? 0.02 : 0 }}
        transition={{ duration: 1, ease: EASE_CALM }}
      />

      <svg
        viewBox={`0 0 ${SCENE_SIZE} ${SCENE_SIZE}`}
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="xMidYMid slice"
      >
        <g transform={`translate(${originX}, ${originY})`}>
          <motion.g
            style={{ transformOrigin: "0px 0px" }}
            animate={{ x: cameraX, y: cameraY, scale: cameraScale }}
            transition={{ duration: DURATION.drift, ease: EASE_CALM }}
          >
            {/* Catches taps/clicks on empty space — "tap elsewhere
             * dismisses" for every tooltip/panel in the scene, including
             * StarExplainPanel which previously had no way to dismiss
             * other than its X button. Rendered first so every real
             * interactive element (painted after it) naturally sits on
             * top for hit-testing. */}
            <rect
              x={-3000}
              y={-3000}
              width={6000}
              height={6000}
              fill="transparent"
              onClick={dismissAll}
              onTouchStart={dismissAll}
            />

            {starfield.map((layer) => (
              <motion.g
                key={layer.depth}
                style={{ transformOrigin: "0px 0px" }}
                animate={{ rotate: 360 }}
                transition={{ duration: layer.driftSeconds, ease: "linear", repeat: Infinity }}
              >
                {layer.stars.map((d, i) => (
                  <circle key={i} cx={d.x} cy={d.y} r={d.r} opacity={d.opacity} fill="#C9C6DA" />
                ))}
              </motion.g>
            ))}

            <NebulaCloud patterns={hiddenPotential} />

            {orbits.map((orbit, i) => (
              <EvidenceOrbitRing key={orbit.key} orbit={orbit} index={i} />
            ))}

            <ConstellationLines
              constellations={constellations}
              stars={visibleStars}
              dismissToken={dismissToken}
              onHoverLine={handleHoverLine}
            />

            {visibleStars.map((star) => (
              <Star
                key={star.id}
                star={star}
                isSelected={selectedStar?.id === star.id}
                boosted={wowActive && star.state === "active"}
                isHighlighted={highlightedStarIds.has(star.id)}
                constellationLabel={starConstellationLabel.get(star.id) ?? null}
                evidenceGraph={evidenceGraph}
                onSelect={setSelectedStar}
              />
            ))}

            <MoonCore
              careerDna={careerDna}
              confidenceScore={confidenceScore}
              understandingStage={understandingStage}
              isThinking={isThinking}
              glowBoost={wowActive ? 1 : 0}
              hypotheses={hypotheses}
              evidenceGraph={evidenceGraph}
              reflectionJournal={reflectionJournal}
              dismissToken={dismissToken}
            />
          </motion.g>
        </g>
      </svg>

      <AnimatePresence>
        {selectedStar && (
          <StarExplainPanel
            star={selectedStar}
            notebookEntries={notebookEntries}
            onClose={() => setSelectedStar(null)}
          />
        )}
      </AnimatePresence>

      <CurrentUnderstandingPanel careerDna={careerDna} className="pointer-events-none absolute bottom-24 left-6" />

      <DiscoveryMilestoneRail
        understandingStage={understandingStage}
        understandingNarrative={understandingNarrative}
        className="pointer-events-none absolute left-6 top-6"
      />

      <div className="absolute inset-x-6 bottom-4">
        <LiveStatusBar understandingStage={understandingStage} notebookEntries={notebookEntries} />
      </div>

      <InsightMoment line={insightMomentLine} onComplete={onDismissInsightMoment} />
    </div>
  );
}
