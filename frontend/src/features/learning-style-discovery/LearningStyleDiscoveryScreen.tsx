import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronDown, ChevronUp, Brain, ShieldAlert, Sparkles } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { PageHeader } from "../../design-system/components/PageHeader";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { LearningStylePattern, LearningStyleTier, LearningStylesResponse } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";

const TIER_LABEL: Record<LearningStyleTier, string> = {
  strong: "Strong",
  growing: "Growing",
  still_emerging: "Still Emerging",
};

const TIER_TONE: Record<LearningStyleTier, "success" | "warm" | "cool"> = {
  strong: "success",
  growing: "warm",
  still_emerging: "cool",
};

const TIER_ORDER: LearningStyleTier[] = ["strong", "growing", "still_emerging"];

const SOURCE_LABELS: Record<string, string> = {
  career_dna: "Career DNA",
  experiment: "Experience Lab",
  reflection: "Reflection",
  evidence_graph: "Conversations",
  hidden_potential: "Hidden Potential",
};

function StyleCard({ pattern }: { pattern: LearningStylePattern }) {
  const [expanded, setExpanded] = useState(false);
  const style = pattern.style;

  const sections: { title: string; items: string[] }[] = [
    { title: "Strengths", items: style.strengths },
    { title: "Where This Excels", items: style.excels_in },
    { title: "Common Struggles", items: style.common_struggles },
    { title: "Study Strategies", items: style.study_strategies },
    { title: "Note-Taking Techniques", items: style.note_taking_techniques },
    { title: "Memory Strategies", items: style.memory_strategies },
    { title: "Active Learning Methods", items: style.active_learning_methods },
    { title: "Project Ideas", items: style.project_ideas },
    { title: "Practice Routines", items: style.practice_routines },
    { title: "Collaboration Techniques", items: style.collaboration_techniques },
    { title: "Learning Environments", items: style.learning_environments },
    { title: "Productivity Systems", items: style.productivity_systems },
    { title: "Recommended Books", items: style.recommended_books },
    { title: "Research-Backed Resources", items: style.research_backed_resources },
    { title: "Online Courses", items: style.online_courses },
    { title: "Communities", items: style.communities },
    { title: "Ways to Strengthen Other Styles", items: style.ways_to_strengthen },
  ];

  return (
    <Surface tone="raised" padding="lg">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm font-medium text-ink">{style.name}</p>
        <Badge tone={TIER_TONE[pattern.tier]}>{TIER_LABEL[pattern.tier]}</Badge>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-ink-muted">{style.description}</p>
      <p className="mt-3 text-sm leading-relaxed text-ink">{pattern.explanation}</p>

      <p className="mt-3 text-[0.65rem] uppercase tracking-[0.1em] text-ink-faint">Why Aureon believes this</p>
      <ul className="mt-1.5 space-y-1">
        {pattern.evidence.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-ink-muted">
            <Badge tone="neutral" className="shrink-0">{SOURCE_LABELS[item.source] ?? item.source}</Badge>
            <span>{item.description}</span>
          </li>
        ))}
      </ul>

      {pattern.recommended_experiments.length > 0 && (
        <div className="mt-3">
          <p className="flex items-center gap-1.5 text-[0.65rem] uppercase tracking-[0.1em] text-accent-soft">
            <Sparkles size={11} /> Recommended Experiments
          </p>
          <ul className="mt-1.5 space-y-1">
            {pattern.recommended_experiments.map((exp) => (
              <li key={exp.id} className="text-xs text-ink-muted">
                <span className="text-accent">＋</span> {exp.title} ({exp.estimated_minutes} min)
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 flex items-center gap-1 text-xs text-accent-soft transition-colors hover:text-accent"
      >
        {expanded ? "Hide study strategies" : "Show study strategies & resources"}
        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {expanded && (
        <div className="mt-4 grid grid-cols-1 gap-4 border-t border-border pt-4 sm:grid-cols-2">
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
          <p className="sm:col-span-2 text-[0.65rem] italic text-ink-faint">{style.source_note}</p>
        </div>
      )}
    </Surface>
  );
}

/**
 * "How do I naturally learn best?" — never a quiz. Inferred from real
 * accumulated evidence across Experience Lab, Reflection Journal,
 * Career DNA, the Evidence Graph, and Hidden Potential's Talent
 * Pattern Engine. A student can show several styles at once; none are
 * exclusive of another. See backend
 * domain/services/learning_style_analysis_service.py.
 */
export function LearningStyleDiscoveryScreen() {
  const studentId = useRef(getCurrentStudentId()).current;
  const [data, setData] = useState<LearningStylesResponse | null>(null);
  // Loading, a genuine fetch failure, and genuinely no styles yet are
  // three different product states.
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  const loadData = useCallback(() => {
    setStatus("loading");
    apiClient
      .get<LearningStylesResponse>(`/v1/students/${studentId}/learning-styles`)
      .then((r) => {
        setData(r);
        setStatus("success");
      })
      .catch(() => setStatus("error"));
  }, [studentId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <PageHeader
        title="Learning Style Discovery"
        description="How you naturally learn best — discovered from what you've actually done, never a self-assessment quiz. You can show several styles at once; none of them lock you in."
      />

      {status === "loading" ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : status === "error" ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={ShieldAlert}
            title="Couldn't Load Learning Styles"
            description="Something went wrong reaching Aureon's servers — this isn't the same as there being nothing here. Try again."
            action={<Button variant="secondary" onClick={loadData}>Retry</Button>}
          />
        </div>
      ) : data && data.patterns.length > 0 ? (
        <div className="mt-8 space-y-8">
          {TIER_ORDER.map((tier) => {
            const inTier = data.patterns.filter((p) => p.tier === tier);
            if (inTier.length === 0) return null;
            return (
              <div key={tier}>
                <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                  {TIER_LABEL[tier]}
                </p>
                <div className="space-y-4">
                  {inTier.map((pattern) => (
                    <StyleCard key={pattern.style.id} pattern={pattern} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Brain}
            title="Still Discovering"
            description="Aureon hasn't gathered enough real evidence yet — a conversation, a reflection, or an Experience Lab activity can all contribute. Learning styles can appear at any point."
          />
        </div>
      )}
    </div>
  );
}
