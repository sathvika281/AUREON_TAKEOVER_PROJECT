import { useState } from "react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  Brain, ChevronDown, Compass, Globe2, Rocket, Search, Sparkles, Users,
} from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import type { CareerDecisionCard } from "../../shared/api/types";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { DecisionExplanationPanel } from "./DecisionExplanationPanel";

/** Same brightness-carries-evidence-strength convention as
 * `MentorMatchCard.tsx`'s GuidingStar — a real, non-decorative signal,
 * not a color chosen for effect. */
const STRENGTH_STYLE: Record<string, { size: number; opacity: number; glow: number }> = {
  Strong: { size: 8, opacity: 1, glow: 9 },
  Growing: { size: 6, opacity: 0.72, glow: 4 },
  "Needs More Evidence": { size: 4, opacity: 0.4, glow: 0 },
};

function ConfidenceDot({ label }: { label: string }) {
  const s = STRENGTH_STYLE[label] ?? STRENGTH_STYLE["Needs More Evidence"];
  return (
    <span
      className="inline-block shrink-0 rounded-full bg-accent-soft"
      style={{ width: s.size, height: s.size, opacity: s.opacity, boxShadow: s.glow ? `0 0 ${s.glow}px rgba(127,176,150,0.7)` : undefined }}
      aria-hidden="true"
    />
  );
}

const VERDICT_LABEL: Record<string, string> = {
  continue_exploring: "Continue Exploring",
  ready_to_shortlist: "Ready to Shortlist",
  hold_for_now: "Hold for Now",
};

const VERDICT_TONE: Record<string, "neutral" | "warm" | "success" | "cool"> = {
  continue_exploring: "cool",
  ready_to_shortlist: "success",
  hold_for_now: "neutral",
};

export function DecisionWorkspaceCardSummary({
  card,
  onSelect,
}: {
  card: CareerDecisionCard;
  onSelect: () => void;
}) {
  const truncated = card.why_it_matters.length > 140 ? `${card.why_it_matters.slice(0, 140)}…` : card.why_it_matters;
  return (
    <button onClick={onSelect} className="text-left">
      <Surface tone="raised" padding="md" className="flex h-full flex-col">
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm font-medium text-ink">{card.career_name}</p>
          <Badge tone={VERDICT_TONE[card.recommendation.verdict]}>{VERDICT_LABEL[card.recommendation.verdict]}</Badge>
        </div>
        <p className="mt-2 text-xs leading-relaxed text-ink-muted">{truncated}</p>
        <div className="mt-auto flex items-center justify-between pt-3">
          <span className="flex items-center gap-2 text-xs text-accent-soft">
            <ConfidenceDot label={card.confidence_label} />
            {card.confidence_band}
          </span>
          <span className="text-xs text-ink-faint">{card.readiness.percent}% progress</span>
        </div>
      </Surface>
    </button>
  );
}

function Section({
  icon: Icon,
  title,
  children,
  defaultOpen = false,
}: {
  icon: typeof Compass;
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="mt-5 border-t border-border pt-4 first:mt-0 first:border-t-0 first:pt-0">
      <button type="button" onClick={() => setOpen((o) => !o)} className="flex w-full items-center justify-between text-left">
        <span className="flex items-center gap-2 text-sm font-medium text-ink">
          <Icon size={15} className="text-accent-soft" />
          {title}
        </span>
        <ChevronDown size={14} className={cn("text-ink-faint transition-transform", open && "rotate-180")} />
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-3">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">{title}</p>
      <ul className="mt-1.5 space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-xs text-ink-muted">• {item}</li>
        ))}
      </ul>
    </div>
  );
}

const READINESS_LABELS: [keyof CareerDecisionCard["readiness"], string][] = [
  ["has_reflection", "Reflection written"],
  ["has_experiment", "Experience completed"],
  ["has_expert_contact", "Talked to an expert"],
  ["has_explored_world", "Explored a related world"],
  ["has_explored_opportunity", "Explored an opportunity"],
  ["has_simulation", "Ran a simulation"],
  ["has_knowledge_circle_engagement", "Engaged a knowledge circle"],
];

export function DecisionWorkspaceCardDetail({
  card,
  onBack,
  onCompare,
  onSimulate,
}: {
  card: CareerDecisionCard;
  onBack: () => void;
  onCompare: (careerId: string) => void;
  onSimulate: (careerId: string) => void;
}) {
  const { candidates, shortlistCandidate, isAnalyzing } = useCareerIntelligenceContext();
  const candidate = candidates.find((c) => c.career_id === card.career_id);
  const isBookmarked = candidate?.is_shortlisted ?? false;

  return (
    <div>
      <button onClick={onBack} className="text-xs text-ink-faint hover:text-ink-muted">← Decision Workspace</button>

      <div className="mt-2 flex items-center justify-between gap-3">
        <h2 className="text-xl font-light text-ink">{card.career_name}</h2>
        <Badge tone={VERDICT_TONE[card.recommendation.verdict]}>{VERDICT_LABEL[card.recommendation.verdict]}</Badge>
      </div>
      <p className="mt-1 text-xs text-ink-faint">{card.one_liner}</p>

      <Section icon={Compass} title="📌 Overview" defaultOpen>
        <p className="text-sm leading-relaxed text-ink">{card.why_it_matters}</p>
        <div className="mt-3 flex items-center gap-2 text-xs text-accent-soft">
          <ConfidenceDot label={card.confidence_label} /> {card.confidence_band}
        </div>
        <div className="mt-4">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-faint">
            Decision Progress — {card.readiness.percent}%
          </p>
          <ul className="mt-1.5 space-y-1 text-xs">
            {READINESS_LABELS.map(([key, label]) => {
              const done = card.readiness[key] as boolean;
              return (
                <li key={key} className={cn(done ? "text-ink" : "text-ink-faint")}>
                  {done ? "✓" : "○"} {label}
                </li>
              );
            })}
          </ul>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-3 text-xs">
          <div><p className="text-ink-faint">2030</p><p className="mt-0.5 text-ink-muted">{card.demand_2030 || "—"}</p></div>
          <div><p className="text-ink-faint">2035</p><p className="mt-0.5 text-ink-muted">{card.demand_2035 || "—"}</p></div>
          <div><p className="text-ink-faint">2040</p><p className="mt-0.5 text-ink-muted">{card.demand_2040 || "—"}</p></div>
        </div>
      </Section>

      <Section icon={Search} title="🔍 Reality Check">
        <div className="grid gap-3 sm:grid-cols-2">
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Daily Work</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.daily_work}</p></div>
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Work-Life Balance</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.work_life_balance}</p></div>
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Stress</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.stress}</p></div>
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Automation Risk</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.automation_risk}</p></div>
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Remote Possibility</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.remote_possibility}</p></div>
          <div><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Travel</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.travel}</p></div>
          <div className="sm:col-span-2"><p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Industry Outlook</p><p className="mt-1 text-xs text-ink-muted">{card.reality_check.industry_outlook}</p></div>
        </div>
        {card.reality_check.salary_ranges.length > 0 && (
          <div className="mt-3 space-y-1.5">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Salary Ranges</p>
            {card.reality_check.salary_ranges.map((s, i) => (
              <p key={i} className="text-xs text-ink-muted">{s.region}: {s.range}{s.note && ` — ${s.note}`}</p>
            ))}
          </div>
        )}
      </Section>

      <Section icon={Brain} title="🧠 Why Aureon Thinks This">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">What Supports This</p>
        {card.reasons_for.length === 0 ? (
          <p className="mt-1 text-xs text-ink-faint">No supporting evidence yet.</p>
        ) : (
          <ul className="mt-1.5 space-y-1">
            {card.reasons_for.map((r, i) => <li key={i} className="text-xs text-ink-muted"><span className="text-accent-soft">＋</span> {r}</li>)}
          </ul>
        )}
        <p className="mt-4 text-[0.65rem] uppercase tracking-widest text-ink-faint">What's Against This</p>
        {card.reasons_against.length === 0 ? (
          <p className="mt-1 text-xs text-ink-faint">No significant concerns raised yet.</p>
        ) : (
          <ul className="mt-1.5 space-y-1">
            {card.reasons_against.map((r, i) => <li key={i} className="text-xs text-danger/85">✕ {r}</li>)}
          </ul>
        )}
        <DecisionExplanationPanel explanation={card.explanation} />
        <ListBlock title="Missing Evidence" items={card.missing_evidence} />
      </Section>

      <Section icon={Sparkles} title="⭐ Your Strengths">
        {card.hidden_strengths.length === 0 && card.relevant_interests.length === 0 && !card.learning_style_pattern && (
          <p className="text-xs text-ink-faint">No strength signal connected to this career yet.</p>
        )}
        {card.hidden_strengths.map((p, i) => (
          <div key={i} className="mt-1">
            <Badge tone="cool">{p.talent.replace(/_/g, " ")}</Badge>
            <p className="mt-1 text-xs text-ink-muted">{p.explanation}</p>
          </div>
        ))}
        {card.relevant_interests.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Relevant Interests</p>
            {card.relevant_interests.map((p, i) => (
              <p key={i} className="mt-1 text-xs text-ink-muted">{p.topic} — {p.explanation}</p>
            ))}
          </div>
        )}
        {card.learning_style_pattern && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Your Learning Style</p>
            <p className="mt-1 text-xs text-ink-muted">
              {card.learning_style_pattern.style.name} ({card.learning_style_pattern.tier.replace(/_/g, " ")}) — {card.learning_style_pattern.explanation}
            </p>
          </div>
        )}
      </Section>

      <Section icon={Globe2} title="🌍 Things to Explore">
        {card.unexplored_worlds.length > 0 && (
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Unexplored Worlds</p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {card.unexplored_worlds.map((w) => <Badge key={w.id} tone="cool">{w.name}</Badge>)}
            </div>
            <Link to="/explore/exposure-universe" className="mt-1.5 inline-block text-xs text-accent-soft hover:text-accent">View all worlds →</Link>
          </div>
        )}
        {card.related_life_missions.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Related Life Missions</p>
            {card.related_life_missions.map((m, i) => (
              <p key={i} className="mt-1 text-xs text-ink-muted">{m.mission.name} ({m.tier.replace(/_/g, " ")})</p>
            ))}
          </div>
        )}
        {card.top_journey_stories.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Journey Stories</p>
            {card.top_journey_stories.map((s) => (
              <p key={s.id} className="mt-1 text-xs text-ink-muted">{s.person_label}</p>
            ))}
            <Link to="/experience/journey-stories" className="mt-1.5 inline-block text-xs text-accent-soft hover:text-accent">View all journey stories →</Link>
          </div>
        )}
        {card.top_knowledge_circles.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Knowledge Circles</p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {card.top_knowledge_circles.map((c) => <Badge key={c.id} tone="cool">{c.name}</Badge>)}
            </div>
            <Link to="/experience/knowledge-circles" className="mt-1.5 inline-block text-xs text-accent-soft hover:text-accent">View all circles →</Link>
          </div>
        )}
        {card.top_opportunities.length > 0 && (
          <div className="mt-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Opportunities</p>
            {card.top_opportunities.map((o, i) => (
              <p key={i} className="mt-1 text-xs text-ink-muted">{o.opportunity.title} — {o.opportunity.organization}</p>
            ))}
            <Link to="/explore/opportunity-equality" className="mt-1.5 inline-block text-xs text-accent-soft hover:text-accent">View all opportunities →</Link>
          </div>
        )}
      </Section>

      <Section icon={Users} title="👥 Learn from People">
        {card.top_experts.length === 0 ? (
          <p className="text-xs text-ink-faint">No matched experts yet.</p>
        ) : (
          <div className="space-y-2">
            {card.top_experts.map((e) => (
              <div key={e.id}>
                <p className="text-sm text-ink">{e.name}</p>
                <p className="text-xs text-ink-faint">{e.profession || e.specialization} · {e.years_experience} years</p>
              </div>
            ))}
          </div>
        )}
        <Link to="/experience/expert-connect" className="mt-2 inline-block text-xs text-accent-soft hover:text-accent">See all experts →</Link>
      </Section>

      <Section icon={Rocket} title="🚀 Your Next Step" defaultOpen>
        {card.decision_gaps.length > 0 && (
          <div className="mb-3">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Before You Decide</p>
            <ul className="mt-1.5 space-y-1">
              {card.decision_gaps.map((g, i) => <li key={i} className="text-xs text-ink-muted">⚠ {g}</li>)}
            </ul>
          </div>
        )}
        {card.next_actions.length > 0 && (
          <ul className="space-y-1.5">
            {card.next_actions.map((a, i) => (
              <li key={i} className="text-sm">
                {a.href ? (
                  <Link to={a.href} className="text-accent-soft hover:text-accent">→ {a.label}</Link>
                ) : (
                  <span className="text-ink-muted">→ {a.label}</span>
                )}
              </li>
            ))}
          </ul>
        )}
        <p className="mt-4 rounded-lg bg-white/[0.03] px-3 py-2 text-xs italic leading-relaxed text-ink-muted">
          {card.recommendation.reason}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link to={`/explore/career-reality/${card.career_id}`}>
            <Button variant="ghost" size="md">Explore this career</Button>
          </Link>
          <Button variant="ghost" size="md" onClick={() => onCompare(card.career_id)}>Compare</Button>
          <Button variant="ghost" size="md" onClick={() => onSimulate(card.career_id)}>Simulate</Button>
          <Link to="/experience/expert-connect">
            <Button variant="ghost" size="md">Talk to an expert</Button>
          </Link>
          <Button
            variant={isBookmarked ? "primary" : "ghost"}
            size="md"
            disabled={isAnalyzing}
            onClick={() => shortlistCandidate(card.career_id)}
          >
            {isBookmarked ? "Bookmarked" : "Bookmark"}
          </Button>
        </div>
      </Section>
    </div>
  );
}
