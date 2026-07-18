import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronUp, Compass, Telescope } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type {
  ExposureUniverseResponse,
  MissingWorldCard as MissingWorldCardType,
  WorldExplorationDetail,
  WorldExplorationLevel,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

const LEVEL_TONE: Record<WorldExplorationLevel, "warm" | "cool" | "success"> = {
  unexplored: "warm",
  partially_explored: "cool",
  explored: "success",
};

const LEVEL_LABEL: Record<WorldExplorationLevel, string> = {
  unexplored: "Limited or None",
  partially_explored: "Growing Exposure",
  explored: "Deep Exposure",
};

/**
 * The full CareerWorld field grid — ported from the old, now-retired
 * MissingWorldsScreen.tsx's `WorldDetail` component, plus new sections
 * (related careers/stories/experts/circle) composed by
 * exposure_universe_service.py. Nothing here is a new catalog — every
 * field is either a real CareerWorld field or a real cross-linked
 * Aureon resource.
 */
function WorldDetailPanel({ detail }: { detail: WorldExplorationDetail }) {
  const world = detail.world;
  const sections: { title: string; items: string[] }[] = [
    { title: "Famous Careers", items: world.famous_careers },
    { title: "Beginner Roadmap", items: world.beginner_roadmap },
    { title: "Required Skills", items: world.required_skills },
    { title: "Common Misconceptions", items: world.misconceptions },
    { title: "Beginner Projects", items: world.beginner_projects },
    { title: "Internships & Pathways", items: world.internships },
    { title: "Colleges & Institutes", items: world.colleges },
    { title: "Companies & Organizations", items: world.companies },
    { title: "Videos & Channels", items: world.videos },
    { title: "Books", items: world.books },
    { title: "Communities", items: world.communities },
  ];

  return (
    <div className="mt-4 space-y-4 border-t border-border pt-4">
      <div className="space-y-3">
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Why It Matters</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{world.why_it_matters}</p>
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Global Importance</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{world.global_importance}</p>
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Future Growth</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{world.future_growth}</p>
        </div>
      </div>

      {detail.related_careers.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Real Careers in This World</p>
          <div className="mt-1.5 flex flex-wrap gap-2">
            {detail.related_careers.map((c) => (
              <Link
                key={c.id}
                to={`/explore/career-reality/${c.id}`}
                className="rounded-full border border-border px-2.5 py-1 text-xs text-ink-muted transition-colors hover:border-accent-soft/50 hover:text-ink"
              >
                {c.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {detail.linked_circle && (
        <Link
          to="/experience/knowledge-circles"
          className="block text-xs text-accent-soft transition-colors hover:text-accent"
        >
          Join the "{detail.linked_circle.name}" Knowledge Circle →
        </Link>
      )}

      {detail.related_stories.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Real Journeys Into This World</p>
          <div className="mt-1.5 space-y-2">
            {detail.related_stories.map((s) => (
              <div key={s.id} className="rounded-lg border border-border px-3 py-2">
                <p className="text-xs font-medium text-ink">{s.person_label}</p>
                <p className="mt-0.5 line-clamp-2 text-xs text-ink-muted">{s.journey}</p>
              </div>
            ))}
            <Link
              to="/experience/journey-stories"
              className="inline-block text-xs text-accent-soft transition-colors hover:text-accent"
            >
              See all Journey Stories →
            </Link>
          </div>
        </div>
      )}

      {detail.related_experts.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">People Working in This World</p>
          <div className="mt-1.5 flex flex-wrap gap-2">
            {detail.related_experts.map((e) => (
              <span key={e.id} className="rounded-full border border-border px-2.5 py-1 text-xs text-ink-muted">
                {e.name} — {e.profession}
              </span>
            ))}
          </div>
          <Link
            to="/experience/expert-connect"
            className="mt-1.5 inline-block text-xs text-accent-soft transition-colors hover:text-accent"
          >
            Talk to an expert →
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {sections.map(
          (section) =>
            section.items.length > 0 && (
              <div key={section.title}>
                <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">{section.title}</p>
                <ul className="mt-1.5 space-y-1">
                  {section.items.map((item, i) => (
                    <li key={i} className="text-xs leading-relaxed text-ink-muted">
                      <span className="text-accent">＋</span> {item}
                    </li>
                  ))}
                </ul>
              </div>
            ),
        )}
      </div>

      <p className="text-[0.65rem] italic text-ink-faint">{world.source_note}</p>
    </div>
  );
}

function MissingWorldCard({
  card,
  isExpanded,
  detail,
  isDetailLoading,
  onToggle,
}: {
  card: MissingWorldCardType;
  isExpanded: boolean;
  detail: WorldExplorationDetail | null;
  isDetailLoading: boolean;
  onToggle: () => void;
}) {
  const previewItems = [...card.world.famous_careers, ...card.world.beginner_projects].slice(0, 4);

  return (
    <Surface tone="raised" padding="lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-ink">{card.world.name}</p>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{card.why_missing}</p>
        </div>
        <Badge tone={LEVEL_TONE[card.level]}>{LEVEL_LABEL[card.level]}</Badge>
      </div>

      {card.world.related_industries.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {card.world.related_industries.map((industry) => (
            <span key={industry} className="rounded-full border border-border px-2 py-0.5 text-[0.65rem] text-ink-faint">
              {industry}
            </span>
          ))}
        </div>
      )}

      {previewItems.length > 0 && (
        <div className="mt-3">
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Inside This World</p>
          <ul className="mt-1 space-y-0.5">
            {previewItems.map((item) => (
              <li key={item} className="text-xs text-ink-muted">
                • {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {card.related_careers.length > 0 && (
        <p className="mt-2 text-xs text-ink-faint">
          Real careers here: {card.related_careers.map((c) => c.name).join(", ")}
        </p>
      )}
      {card.linked_circle && (
        <p className="mt-1 text-xs text-ink-faint">Has a Knowledge Circle: {card.linked_circle.name}</p>
      )}

      <button
        onClick={onToggle}
        className="mt-4 flex items-center gap-1.5 text-xs font-medium text-accent-soft transition-colors hover:text-accent"
      >
        {isExpanded ? "Hide" : "Explore This World"}
        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isExpanded && (
        isDetailLoading || !detail ? (
          <p className="mt-4 border-t border-border pt-4 text-xs text-ink-faint">Loading…</p>
        ) : (
          <WorldDetailPanel detail={detail} />
        )
      )}
    </Surface>
  );
}

/**
 * Exposure Universe — the single, unified successor to the former
 * separate "Missing Worlds" and "Exposure Universe" destinations.
 * Missing Worlds detection (missing_worlds_engine.py) is DETECTION;
 * Exposure Universe's own unfamiliar-career selection
 * (exposure_recommendation.py) is DISCOVERY + ACTION — composed here by
 * exposure_universe_service.py into one screen, never re-derived.
 * "Missing" always means lack of meaningful exposure, never a
 * recommendation to pursue a career.
 */
export function ExposureUniverseScreen() {
  const studentId = useRef(getCurrentStudentId()).current;
  const [data, setData] = useState<ExposureUniverseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [expandedWorldId, setExpandedWorldId] = useState<string | null>(null);
  const [worldDetails, setWorldDetails] = useState<Record<string, WorldExplorationDetail>>({});
  const [loadingWorldId, setLoadingWorldId] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<ExposureUniverseResponse>(`/v1/students/${studentId}/exposure-universe`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setIsLoading(false));
  }, [studentId]);

  const toggleWorld = useCallback(
    (worldId: string) => {
      if (expandedWorldId === worldId) {
        setExpandedWorldId(null);
        return;
      }
      setExpandedWorldId(worldId);
      if (!worldDetails[worldId]) {
        setLoadingWorldId(worldId);
        apiClient
          .get<WorldExplorationDetail>(`/v1/students/${studentId}/exposure-universe/worlds/${worldId}`)
          .then((detail) => setWorldDetails((prev) => ({ ...prev, [worldId]: detail })))
          .catch(() => {})
          .finally(() => setLoadingWorldId(null));
      }
    },
    [studentId, expandedWorldId, worldDetails],
  );

  const dismiss = useCallback(
    (careerId: string) => {
      setDismissed((prev) => new Set(prev).add(careerId));
      void apiClient.post(`/v1/students/${studentId}/exposure-universe/interact`, {
        career_id: careerId,
        interaction: "dismissed",
      });
    },
    [studentId],
  );

  const open = useCallback(
    (careerId: string) => {
      void apiClient.post(`/v1/students/${studentId}/exposure-universe/interact`, {
        career_id: careerId,
        interaction: "opened",
      });
    },
    [studentId],
  );

  const visiblePossibilities = (data?.suggestions ?? []).filter((s) => !dismissed.has(s.career.id));

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Exposure Universe</h1>
      <p className="mt-2 text-sm text-ink-muted">
        The parts of the career universe you know, the parts you may never have encountered, and specific
        possibilities worth a look — never a recommendation, just an honest map of what's out there.
      </p>

      {isLoading || !data ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : (
        <>
          {/* 1. Your Exposure Map */}
          {(data.exposure_map.engaged.length > 0 || data.exposure_map.limited_or_none.length > 0) && (
            <section className="mt-8">
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Your Exposure Map
              </p>
              <Surface tone="neutral" padding="md">
                {data.exposure_map.engaged.length > 0 && (
                  <div>
                    <p className="text-xs text-ink-faint">You&rsquo;ve explored</p>
                    <div className="mt-1.5 flex flex-wrap gap-2">
                      {data.exposure_map.engaged.map((s) => (
                        <span key={s.world_name} className="flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-xs">
                          <span className="text-ink">{s.world_name}</span>
                          <Badge tone={LEVEL_TONE[s.level]}>{LEVEL_LABEL[s.level]}</Badge>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {data.exposure_map.limited_or_none.length > 0 && (
                  <div className={data.exposure_map.engaged.length > 0 ? "mt-4 border-t border-border pt-4" : ""}>
                    <p className="text-xs text-ink-faint">You have limited or no meaningful exposure to</p>
                    <div className="mt-1.5 flex flex-wrap gap-2">
                      {data.exposure_map.limited_or_none.map((s) => (
                        <span key={s.world_name} className="rounded-full border border-border px-2.5 py-1 text-xs text-ink-muted">
                          {s.world_name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </Surface>
            </section>
          )}

          {/* 2. Your Missing Worlds */}
          {data.missing_worlds.length > 0 && (
            <section className="mt-8">
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Worlds You Haven&rsquo;t Meaningfully Explored
              </p>
              <div className="space-y-3">
                {data.missing_worlds.map((card) => (
                  <MissingWorldCard
                    key={card.world.id}
                    card={card}
                    isExpanded={expandedWorldId === card.world.id}
                    detail={worldDetails[card.world.id] ?? null}
                    isDetailLoading={loadingWorldId === card.world.id}
                    onToggle={() => toggleWorld(card.world.id)}
                  />
                ))}
              </div>
            </section>
          )}

          {/* 3. Possibilities You May Not Know */}
          <section className="mt-8">
            <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
              Possibilities You May Not Know
            </p>
            {visiblePossibilities.length === 0 ? (
              <EmptyStatePanel
                icon={Telescope}
                title="Nothing New Right Now"
                description="You've seen everything Aureon currently has to show you here — check back later as the catalog grows."
              />
            ) : (
              <div className="space-y-4">
                {visiblePossibilities.map((suggestion) => (
                  <Surface key={suggestion.career.id} tone="raised" padding="lg">
                    <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
                      <Telescope size={11} className="mr-1.5 inline" />
                      A World You Might Not Know
                    </p>
                    {suggestion.related_missing_world && (
                      <p className="mt-1 flex items-center gap-1 text-xs text-ink-faint">
                        <Compass size={11} /> Connects to the {suggestion.related_missing_world} world you haven&rsquo;t
                        explored
                      </p>
                    )}
                    <p className="mt-2 text-sm leading-relaxed text-ink">{suggestion.curiosity_hook}</p>
                    <p className="mt-3 text-sm font-medium text-ink">{suggestion.career.name}</p>
                    <p className="mt-1 text-xs text-ink-muted">{suggestion.career.one_liner}</p>

                    {suggestion.mini_introduction && (
                      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{suggestion.mini_introduction}</p>
                    )}

                    {(suggestion.watch.length > 0 ||
                      suggestion.read.length > 0 ||
                      suggestion.build.length > 0 ||
                      suggestion.join.length > 0) && (
                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        {suggestion.watch.length > 0 && (
                          <div>
                            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Watch</p>
                            <ul className="mt-1 space-y-0.5">
                              {suggestion.watch.map((w) => (
                                <li key={w} className="text-xs text-ink-muted">{w}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {suggestion.read.length > 0 && (
                          <div>
                            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Read</p>
                            <ul className="mt-1 space-y-0.5">
                              {suggestion.read.map((r) => (
                                <li key={r} className="text-xs text-ink-muted">{r}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {suggestion.build.length > 0 && (
                          <div>
                            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Build</p>
                            <ul className="mt-1 space-y-0.5">
                              {suggestion.build.map((b) => (
                                <li key={b} className="text-xs text-ink-muted">{b}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {suggestion.join.length > 0 && (
                          <div>
                            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Join</p>
                            <ul className="mt-1 space-y-0.5">
                              {suggestion.join.map((j) => (
                                <li key={j} className="text-xs text-ink-muted">{j}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {suggestion.quick_project && (
                      <p className="mt-3 text-xs text-ink-muted">
                        <span className="text-ink-faint">Quick project to try: </span>
                        {suggestion.quick_project}
                      </p>
                    )}

                    {suggestion.reflect_prompt && (
                      <p className="mt-3 text-xs italic text-ink-faint">{suggestion.reflect_prompt}</p>
                    )}

                    {suggestion.suggested_experience && (
                      <Link
                        to="/discover/experience-lab"
                        className="mt-3 inline-block text-xs text-accent-soft transition-colors hover:text-accent"
                      >
                        Try "{suggestion.suggested_experience.title}" in Experience Lab →
                      </Link>
                    )}

                    <div className="mt-4 flex items-center gap-4">
                      <Link
                        to={`/explore/career-reality/${suggestion.career.id}`}
                        onClick={() => open(suggestion.career.id)}
                        className="text-xs font-medium text-accent-soft transition-colors hover:text-accent"
                      >
                        See what this world is like
                      </Link>
                      <button
                        onClick={() => dismiss(suggestion.career.id)}
                        className="text-xs text-ink-faint transition-colors hover:text-ink-muted"
                      >
                        Not for me
                      </button>
                    </div>
                  </Surface>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
