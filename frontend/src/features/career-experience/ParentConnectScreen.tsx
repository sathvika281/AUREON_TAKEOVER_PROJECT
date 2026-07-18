import { useEffect, useMemo, useState } from "react";
import { Globe, HeartHandshake, MessageCircleQuestion, Users2 } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { cn } from "../../design-system/cn";
import { apiClient } from "../../shared/api/client";
import type {
  CareerSummary,
  ParentCareerView,
  ParentQuestion,
  ParentQuestionCategory,
  ParentQuestionsResponse,
} from "../../shared/api/types";
import { ExpertConnectTabs } from "./ExpertConnectTabs";
import { ParentLanguageProvider, SUPPORTED_PARENT_LANGUAGES, useParentLanguage } from "./ParentLanguageContext";

const CATEGORIES: { value: ParentQuestionCategory; label: string }[] = [
  { value: "salary", label: "Salary" },
  { value: "safety", label: "Safety" },
  { value: "stability", label: "Stability" },
  { value: "work_life_balance", label: "Work-Life Balance" },
  { value: "growth", label: "Growth" },
  { value: "international", label: "International" },
  { value: "career_switching", label: "Career Switching" },
  { value: "other", label: "Other" },
];

function PillToggle({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-3.5 py-1.5 text-xs transition-colors",
        active
          ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
          : "border-border text-ink-muted hover:border-border-strong hover:text-ink",
      )}
    >
      {label}
    </button>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <section className="mt-6">
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <ul className="space-y-1.5 text-sm text-ink-muted">
        {items.map((item, i) => (
          <li key={i}>• {item}</li>
        ))}
      </ul>
    </section>
  );
}

function ParagraphSection({ title, text }: { title: string; text: string }) {
  if (!text) return null;
  return (
    <section className="mt-6">
      <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
      <p className="text-sm leading-relaxed text-ink-muted">{text}</p>
    </section>
  );
}

/**
 * The first thing a parent sees — large, simple, native-script buttons.
 * No text-to-speech/"listen" control here: no real speech infrastructure
 * exists in this codebase yet, and a button that doesn't work would be
 * worse than no button (see docs — documented as a future accessibility
 * enhancement, not faked).
 */
function LanguageChoiceScreen({ onChoose }: { onChoose: (code: "en" | "hi" | "te") => void }) {
  return (
    <div className="mx-auto max-w-md px-6 py-16 text-center">
      <Globe size={28} className="mx-auto text-accent-soft" />
      <h1 className="mt-4 text-2xl font-light text-ink">Choose your language</h1>
      <p className="mt-2 text-base text-ink-muted">अपनी भाषा चुनें · మీ భాషను ఎంచుకోండి</p>
      <div className="mt-8 space-y-3">
        {SUPPORTED_PARENT_LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            onClick={() => onChoose(lang.code)}
            className="block w-full rounded-xl border border-border-strong bg-surface-raised py-4 text-xl text-ink transition-colors hover:border-accent-soft hover:text-accent-soft"
          >
            {lang.nativeLabel}
          </button>
        ))}
      </div>
    </div>
  );
}

function ParentConnectContent() {
  const { language, setLanguage, resetLanguage } = useParentLanguage();

  const [catalog, setCatalog] = useState<CareerSummary[]>([]);
  const [query, setQuery] = useState("");
  const [selectedCareerId, setSelectedCareerId] = useState<string | null>(null);
  const [view, setView] = useState<ParentCareerView | null>(null);
  const [isLoadingView, setIsLoadingView] = useState(false);

  const [categoryFilter, setCategoryFilter] = useState<ParentQuestionCategory | null>(null);
  const [questions, setQuestions] = useState<ParentQuestion[]>([]);

  useEffect(() => {
    apiClient.get<CareerSummary[]>("/v1/careers").then(setCatalog).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedCareerId || !language) {
      setView(null);
      return;
    }
    setIsLoadingView(true);
    apiClient
      .get<ParentCareerView>(`/v1/careers/${selectedCareerId}/parent-view?language=${language}`)
      .then(setView)
      .catch(() => setView(null))
      .finally(() => setIsLoadingView(false));
  }, [selectedCareerId, language]);

  useEffect(() => {
    if (!language) return;
    const params = new URLSearchParams({ language });
    if (categoryFilter) params.set("category", categoryFilter);
    apiClient
      .get<ParentQuestionsResponse>(`/v1/parent-questions?${params.toString()}`)
      .then((r) => setQuestions(r.questions))
      .catch(() => {});
  }, [categoryFilter, language]);

  const filteredCatalog = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter((c) => c.name.toLowerCase().includes(q) || c.industry.toLowerCase().includes(q));
  }, [catalog, query]);

  if (!language) {
    return <LanguageChoiceScreen onChoose={setLanguage} />;
  }

  const currentLanguageLabel = SUPPORTED_PARENT_LANGUAGES.find((l) => l.code === language)?.nativeLabel;

  const LanguageSwitcher = (
    <div className="mt-3 flex items-center gap-2 text-xs text-ink-faint">
      <Globe size={12} />
      <span>{currentLanguageLabel}</span>
      <button onClick={resetLanguage} className="text-accent-soft hover:text-accent">
        Change
      </button>
    </div>
  );

  if (selectedCareerId) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <ExpertConnectTabs />
        <button onClick={() => setSelectedCareerId(null)} className="mt-6 text-xs text-ink-faint hover:text-ink-muted">
          ← Parent Connect
        </button>

        {isLoadingView && <p className="mt-6 text-sm text-ink-faint">Loading…</p>}

        {view && (
          <>
            <h1 className="mt-2 text-2xl font-light text-ink">{view.career_name}</h1>
            <p className="mt-1 text-sm text-ink-muted">{view.one_liner}</p>

            <ListSection title="Common Misconceptions" items={view.common_misconceptions} />
            <ParagraphSection title="Earning Reality" text={view.earning_reality} />
            <ParagraphSection title="Career Stability" text={view.career_stability} />
            <ParagraphSection title="Work-Life Balance" text={view.work_life_balance} />
            <ParagraphSection title="Growth Opportunities" text={view.growth_opportunities} />
            <ListSection title="Educational Pathways" items={view.educational_pathways} />
            <ListSection title="Alternative Routes" items={view.alternative_routes} />
            <ParagraphSection title="Global Demand" text={view.global_demand} />
            <ListSection title="Risks" items={view.risks} />
            <ListSection title="Opportunities" items={view.opportunities} />

            {view.salary_ranges.length > 0 && (
              <section className="mt-6">
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Salary Ranges</p>
                <div className="space-y-2">
                  {view.salary_ranges.map((s, i) => (
                    <Surface key={i} tone="raised" padding="sm">
                      <p className="text-sm text-ink">{s.region}: {s.range}</p>
                      {s.note && <p className="mt-0.5 text-xs text-ink-faint">{s.note}</p>}
                    </Surface>
                  ))}
                </div>
              </section>
            )}

            {(view.demand_2030 || view.demand_2035 || view.demand_2040) && (
              <section className="mt-6">
                <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Future Demand</p>
                <div className="space-y-2 text-sm text-ink-muted">
                  {view.demand_2030 && <p><span className="text-ink-faint">2030 — </span>{view.demand_2030}</p>}
                  {view.demand_2035 && <p><span className="text-ink-faint">2035 — </span>{view.demand_2035}</p>}
                  {view.demand_2040 && <p><span className="text-ink-faint">2040 — </span>{view.demand_2040}</p>}
                </div>
              </section>
            )}

            {view.expert_advice.length > 0 && (
              <section className="mt-8">
                <div className="mb-2 flex items-center gap-1.5 px-1 text-accent-soft">
                  <HeartHandshake size={13} />
                  <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em]">Advice From Real Experts</p>
                </div>
                <div className="space-y-3">
                  {view.expert_advice.map((a) => (
                    <Surface key={a.expert_id} tone="raised" padding="md">
                      <p className="text-sm font-medium text-ink">{a.expert_name}</p>
                      <p className="text-xs text-ink-faint">{a.expert_profession}</p>
                      <p className="mt-2 text-sm leading-relaxed text-ink-muted">{a.advice_for_parents}</p>
                      {a.faqs.length > 0 && (
                        <div className="mt-3 space-y-2 border-t border-border pt-3">
                          {a.faqs.map((f, i) => (
                            <div key={i}>
                              <p className="text-xs font-medium text-ink">{f.question}</p>
                              <p className="text-xs text-ink-muted">{f.answer}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </Surface>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <ExpertConnectTabs />
      <h1 className="mt-6 text-2xl font-light text-ink">Parent Connect</h1>
      <p className="mt-2 text-sm text-ink-muted">
        How can I understand this career before we decide together? Pick a career for a simple,
        honest explanation, or browse real answers to common parent questions below.
      </p>
      {LanguageSwitcher}

      <Link
        to="/experience/shared-sessions"
        className="mt-4 inline-flex items-center gap-1.5 text-xs text-accent-soft hover:text-accent"
      >
        <Users2 size={13} /> Schedule a Joint Session with an expert →
      </Link>

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search a career by name or industry…"
        className="mt-6"
      />

      {filteredCatalog.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel icon={HeartHandshake} title="No Careers Found" description="Try a different search term." />
        </div>
      ) : (
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {filteredCatalog.map((career) => (
            <button key={career.id} onClick={() => setSelectedCareerId(career.id)} className="text-left">
              <Surface tone="raised" padding="md">
                <p className="text-sm font-medium text-ink">{career.name}</p>
                <p className="mt-1 text-xs text-ink-faint">{career.industry}</p>
                <p className="mt-2 text-xs text-ink-muted">{career.one_liner}</p>
              </Surface>
            </button>
          ))}
        </div>
      )}

      <div className="mt-12">
        <div className="mb-2 flex items-center gap-1.5 px-1 text-ink-faint">
          <MessageCircleQuestion size={13} />
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em]">Parent Questions</p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          <PillToggle label="All" active={categoryFilter === null} onClick={() => setCategoryFilter(null)} />
          {CATEGORIES.map((c) => (
            <PillToggle
              key={c.value}
              label={c.label}
              active={categoryFilter === c.value}
              onClick={() => setCategoryFilter(categoryFilter === c.value ? null : c.value)}
            />
          ))}
        </div>

        {questions.length === 0 ? (
          <div className="mt-6">
            <EmptyStatePanel icon={MessageCircleQuestion} title="No Questions Yet" description="Try a different category." />
          </div>
        ) : (
          <div className="mt-6 space-y-3">
            {questions.map((q) => (
              <Surface key={q.id} tone="raised" padding="md">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium text-ink">{q.question}</p>
                  <Badge tone="cool">{q.category.replace(/_/g, " ")}</Badge>
                </div>
                {q.expert_response && <p className="mt-2 text-sm text-ink-muted">{q.expert_response}</p>}
              </Surface>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Parent Connect (Connect restructuring) — the tab Parent Connect
 * folded into inside Expert Connect, no longer a separate top-level
 * destination. Begins with a real language choice (English/Hindi/
 * Telugu), backed by genuinely translated career-guide and
 * parent-question content (see scripts/translate_parent_connect_content.py),
 * not just a translated selector over English content. Backend models
 * stay named "Parent" throughout — this is simply the product name.
 */
export function ParentConnectScreen() {
  return (
    <ParentLanguageProvider>
      <ParentConnectContent />
    </ParentLanguageProvider>
  );
}
