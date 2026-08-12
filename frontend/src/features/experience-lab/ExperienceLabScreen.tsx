import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  FlaskConical,
  Minus,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { PageHeader } from "../../design-system/components/PageHeader";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type {
  EmergingMission,
  Experiment,
  ExperimentEvidenceRequest,
  ExperienceLabViewResponse,
  LifeMission,
  MissionTier,
  MissionTrend,
} from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

const CATEGORY_LABELS: Record<string, string> = {
  read_abstract: "Read & Think",
  debug_code: "Debug",
  analyze_problem: "Analyze",
  observe_design: "Observe",
  reflect_on_workflow: "Reflect",
};

const EVIDENCE_FLAGS: { key: keyof Omit<ExperimentEvidenceRequest, "reflection">; label: string }[] = [
  { key: "enjoyment", label: "I enjoyed this" },
  { key: "curiosity", label: "I wanted to know more" },
  { key: "persistence", label: "I kept going even when it was hard" },
  { key: "confidence", label: "I felt confident doing this" },
  { key: "frustration", label: "I felt frustrated" },
];

const EMPTY_EVIDENCE: ExperimentEvidenceRequest = {
  enjoyment: false,
  curiosity: false,
  frustration: false,
  persistence: false,
  confidence: false,
  reflection: "",
};

const TIER_LABEL: Record<MissionTier, string> = {
  still_emerging: "Just Emerging",
  growing: "Growing Resonance",
  strong: "Strong Resonance",
};

const TIER_TONE: Record<MissionTier, "cool" | "warm" | "success"> = {
  still_emerging: "cool",
  growing: "warm",
  strong: "success",
};

const TREND_ICON: Record<MissionTrend, typeof TrendingUp> = {
  emerging: TrendingUp,
  steady: Minus,
  fading: TrendingDown,
  not_enough_evidence: Minus,
};

const TREND_LABEL: Record<MissionTrend, string> = {
  emerging: "Emerging",
  steady: "Steady",
  fading: "Fading",
  not_enough_evidence: "Not enough evidence yet",
};

const SOURCE_LABELS: Record<string, string> = {
  career_dna: "Career DNA",
  experiment: "an experience",
  reflection: "a reflection",
  evidence_graph: "a conversation",
};

function MissionContent({ mission }: { mission: LifeMission }) {
  const sections: { title: string; items: string[] }[] = [
    { title: "Famous People", items: mission.famous_people },
    { title: "Organizations", items: mission.organizations },
    { title: "Companies", items: mission.companies },
    { title: "Nonprofits", items: mission.nonprofits },
    { title: "Books", items: mission.books },
    { title: "Documentaries", items: mission.documentaries },
    { title: "Podcasts", items: mission.podcasts },
    { title: "Communities", items: mission.communities },
    { title: "Real-World Examples", items: mission.real_world_examples },
    { title: "Suggested Careers", items: mission.suggested_careers },
    { title: "Projects to Try", items: mission.projects },
    { title: "Volunteering Opportunities", items: mission.volunteering_opportunities },
    { title: "Research Areas", items: mission.research_areas },
    { title: "Startup Ideas", items: mission.startup_ideas },
  ];

  return (
    <div className="mt-4 space-y-4 border-t border-border pt-4">
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
      <p className="text-[0.65rem] italic text-ink-faint">{mission.source_note}</p>
    </div>
  );
}

function EmergingMissionCard({
  emerging,
  onTrySuggested,
}: {
  emerging: EmergingMission;
  onTrySuggested: (experimentId: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const TrendIcon = TREND_ICON[emerging.trend];

  return (
    <Surface tone="raised" padding="lg">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm font-medium text-ink">{emerging.mission.name}</p>
        <div className="flex shrink-0 items-center gap-2">
          <Badge tone={TIER_TONE[emerging.tier]}>{TIER_LABEL[emerging.tier]}</Badge>
          <span className="flex items-center gap-1 text-[0.65rem] text-ink-faint" title={TREND_LABEL[emerging.trend]}>
            <TrendIcon size={12} />
          </span>
        </div>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-ink">{emerging.explanation}</p>

      <p className="mt-3 text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Why Aureon believes this</p>
      <ul className="mt-1.5 space-y-1">
        {emerging.evidence.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-ink-muted">
            <Badge tone="neutral" className="shrink-0">{SOURCE_LABELS[item.source] ?? item.source}</Badge>
            <span>{item.description}</span>
          </li>
        ))}
      </ul>

      {emerging.suggested_experience && (
        <div className="mt-4 rounded-lg border border-accent-soft/30 bg-accent/5 p-3">
          <p className="text-[0.65rem] uppercase tracking-[0.1em] text-accent-soft">Suggested Experience</p>
          <p className="mt-1 text-sm text-ink">{emerging.suggested_experience.title}</p>
          <button
            onClick={() => onTrySuggested(emerging.suggested_experience!.id)}
            className="mt-2 rounded-lg border border-accent-soft/40 px-3 py-1.5 text-xs font-medium text-accent-soft transition-colors hover:border-accent-soft hover:text-accent"
          >
            Try This Experience
          </button>
        </div>
      )}

      <button
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 flex items-center gap-1 text-xs text-accent-soft transition-colors hover:text-accent"
      >
        {expanded ? "Hide details" : "Show more about this mission"}
        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>
      {expanded && <MissionContent mission={emerging.mission} />}
    </Surface>
  );
}

function ExperienceCard({
  experiment,
  isCompleted,
  isActive,
  evidence,
  isSubmitting,
  onStart,
  onToggleFlag,
  onReflectionChange,
  onSubmit,
  onCancel,
}: {
  experiment: Experiment;
  isCompleted: boolean;
  isActive: boolean;
  evidence: ExperimentEvidenceRequest;
  isSubmitting: boolean;
  onStart: (id: string) => void;
  onToggleFlag: (key: keyof Omit<ExperimentEvidenceRequest, "reflection">) => void;
  onReflectionChange: (value: string) => void;
  onSubmit: (id: string) => void;
  onCancel: () => void;
}) {
  return (
    <Surface id={`experience-${experiment.id}`} tone="raised" padding="lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-ink">{experiment.title}</p>
          <p className="mt-1 text-xs text-ink-faint">
            {experiment.related_world} · {experiment.estimated_minutes} min
          </p>
        </div>
        <Badge tone="cool">{CATEGORY_LABELS[experiment.category] ?? experiment.category}</Badge>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{experiment.description}</p>

      {isCompleted ? (
        <Badge tone="success" className="mt-4">Completed</Badge>
      ) : isActive ? (
        <div className="mt-4 space-y-4 border-t border-border pt-4">
          <p className="whitespace-pre-line text-sm leading-relaxed text-ink">{experiment.instructions}</p>
          <p className="text-sm italic text-ink-muted">{experiment.reflection_prompt}</p>

          <div className="flex flex-wrap gap-2">
            {EVIDENCE_FLAGS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => onToggleFlag(key)}
                className={`rounded-full border px-3 py-1.5 text-xs transition-colors ${
                  evidence[key]
                    ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                    : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <textarea
            value={evidence.reflection}
            onChange={(e) => onReflectionChange(e.target.value)}
            placeholder="Anything else you noticed about yourself? (optional)"
            rows={3}
            className="w-full resize-none rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-border-strong focus:outline-none"
          />

          <div className="flex items-center gap-4">
            <button
              onClick={() => onSubmit(experiment.id)}
              disabled={isSubmitting}
              className="rounded-lg bg-accent px-4 py-2 text-xs font-medium tracking-wide text-ink transition-colors hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? "Saving…" : "Done — Save What I Noticed"}
            </button>
            <button onClick={onCancel} className="text-xs text-ink-faint transition-colors hover:text-ink-muted">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <Button variant="secondary" className="mt-4" onClick={() => onStart(experiment.id)}>
          Try This
        </Button>
      )}
    </Surface>
  );
}

/** A compact, non-interactive highlight — the real, full interactive
 * card lives once in its category section below. Avoids rendering the
 * same experiment as two independent interactive instances (which would
 * both enter "active" state together, confusingly, since activeId is
 * shared screen state by design). */
function RecommendedPreviewCard({
  experiment,
  onTry,
}: {
  experiment: Experiment;
  onTry: (id: string) => void;
}) {
  return (
    <Surface tone="raised" padding="lg">
      <p className="mb-2 flex items-center gap-1.5 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">
        <Sparkles size={11} /> Aureon Suggests Starting Here
      </p>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-ink">{experiment.title}</p>
          <p className="mt-1 text-xs text-ink-faint">
            {experiment.related_world} · {experiment.estimated_minutes} min
          </p>
        </div>
        <Badge tone="cool">{CATEGORY_LABELS[experiment.category] ?? experiment.category}</Badge>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{experiment.description}</p>
      <Button variant="secondary" className="mt-4" onClick={() => onTry(experiment.id)}>
        Try This
      </Button>
    </Surface>
  );
}

function SectionEmptyNote({ children }: { children: React.ReactNode }) {
  return <p className="rounded-lg border border-border/60 px-4 py-3 text-xs text-ink-faint">{children}</p>;
}

/**
 * Experience Lab — the single unified Discover destination for "try
 * something real." Merges what used to be two separate destinations:
 * Career Experiences (small, real activities tied to a world/career)
 * and Life Missions (what kind of real-world impact resonates with the
 * student). A mission's resonance is now shown as "Your Emerging
 * Missions," paired with a real, curated Mission Experience the student
 * can actually try — never a fabricated confidence bump from merely
 * completing something (see backend domain/services/
 * life_mission_engine.py::_has_genuine_engagement). Backend intelligence
 * stays fully separate (experiment_result.py / life_mission_engine.py);
 * this screen is purely a unified presentation over
 * domain/services/experience_lab_service.py's composed view.
 */
export function ExperienceLabScreen() {
  const studentId = useRef(getCurrentStudentId()).current;

  const [view, setView] = useState<ExperienceLabViewResponse | null>(null);
  // Loading, a genuine fetch failure, and a successful-but-empty response
  // are three different product states — see JourneyStoriesScreen's own
  // "Sprint 4 fix" comment for the same principle. Previously this screen
  // used `!isLoading && view && ...` for its empty check, which meant a
  // failed request (view stays null) matched neither the loading, empty,
  // nor populated branch — the screen silently rendered nothing below
  // the title.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [activeId, setActiveId] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<ExperimentEvidenceRequest>(EMPTY_EVIDENCE);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());

  const loadView = useCallback(() => {
    setStatus("loading");
    apiClient
      .get<ExperienceLabViewResponse>(`/v1/students/${studentId}/experience-lab`)
      .then((r) => {
        setView(r);
        setCompletedIds(new Set(r.completed_experiment_ids));
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [studentId]);

  useEffect(() => {
    loadView();
  }, [loadView]);

  const startExperiment = (id: string) => {
    setActiveId(id);
    setEvidence(EMPTY_EVIDENCE);
  };

  const trySuggested = (id: string) => {
    startExperiment(id);
    document.getElementById(`experience-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const toggleFlag = (key: keyof Omit<ExperimentEvidenceRequest, "reflection">) => {
    setEvidence((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const submitEvidence = async (experimentId: string) => {
    setIsSubmitting(true);
    try {
      await apiClient.post(`/v1/students/${studentId}/experiments/${experimentId}/complete`, evidence);
      setCompletedIds((prev) => new Set(prev).add(experimentId));
      setActiveId(null);
    } catch {
      // Left active on failure so the student's answers aren't lost.
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderExperience = (experiment: Experiment) => (
    <ExperienceCard
      key={experiment.id}
      experiment={experiment}
      isCompleted={completedIds.has(experiment.id)}
      isActive={activeId === experiment.id}
      evidence={evidence}
      isSubmitting={isSubmitting}
      onStart={startExperiment}
      onToggleFlag={toggleFlag}
      onReflectionChange={(value) => setEvidence((prev) => ({ ...prev, reflection: value }))}
      onSubmit={submitEvidence}
      onCancel={() => setActiveId(null)}
    />
  );

  const isEmpty =
    status === "success" &&
    view &&
    view.recommended.length === 0 &&
    view.mission_experiences.length === 0 &&
    view.career_experiences.length === 0;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <PageHeader
        title="Experience Lab"
        description="Don't just read about possibilities — try them. Small, real activities, some tied to careers, some tied to the kind of impact you care about. What you notice about yourself while doing one becomes real evidence Aureon can learn from."
      />

      {status === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : status === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Experience Lab"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
            action={<Button variant="secondary" onClick={loadView}>Retry</Button>}
          />
        </div>
      ) : isEmpty ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={FlaskConical}
            title="No Experiences Yet"
            description="Aureon's Experience Lab catalog hasn't been populated yet — check back soon."
          />
        </div>
      ) : (
        view && (
          <div className="mt-8 space-y-10">
            {view.recommended.length > 0 && (
              <section>
                <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  Recommended for You
                </p>
                <div className="space-y-4">
                  {view.recommended.map((e) => (
                    <RecommendedPreviewCard key={e.id} experiment={e} onTry={trySuggested} />
                  ))}
                </div>
              </section>
            )}

            <section>
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Your Emerging Missions
              </p>
              {view.emerging_missions.length > 0 ? (
                <div className="space-y-4">
                  {view.emerging_missions.map((em) => (
                    <EmergingMissionCard key={em.mission.id} emerging={em} onTrySuggested={trySuggested} />
                  ))}
                </div>
              ) : (
                <SectionEmptyNote>
                  Nothing yet — every conversation, reflection, and completed experience helps Aureon
                  notice what kind of real-world impact might matter to you.
                </SectionEmptyNote>
              )}
            </section>

            <section>
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Mission Experiences
              </p>
              {view.mission_experiences.length > 0 ? (
                <div className="space-y-4">{view.mission_experiences.map((e) => renderExperience(e))}</div>
              ) : (
                <SectionEmptyNote>More mission-connected experiences are on their way.</SectionEmptyNote>
              )}
            </section>

            <section>
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Career Experiences
              </p>
              {view.career_experiences.length > 0 ? (
                <div className="space-y-4">{view.career_experiences.map((e) => renderExperience(e))}</div>
              ) : (
                <SectionEmptyNote>More career-connected experiences are on their way.</SectionEmptyNote>
              )}
            </section>

            {view.completed.length > 0 && (
              <section>
                <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  Completed Experiences
                </p>
                <div className="space-y-2">
                  {view.completed.map((c) => (
                    <Surface key={c.id} tone="neutral" padding="md">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium text-ink">{c.experiment_title}</p>
                          <p className="mt-1 text-xs text-ink-faint">
                            {c.related_world} · {new Date(c.completed_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge tone="success">Completed</Badge>
                      </div>
                    </Surface>
                  ))}
                </div>
              </section>
            )}
          </div>
        )
      )}
    </div>
  );
}
