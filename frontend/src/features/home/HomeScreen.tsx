import { Link } from "react-router-dom";

import { Field } from "../../design-system/components/Field";
import { Surface } from "../../design-system/components/Surface";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { useCareerExplorationContext } from "../career-exploration/CareerExplorationContext";
import { useDecisionContext } from "../decision/DecisionContext";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { HypothesisCard } from "../discovery/notebook/HypothesisCard";
import { relativeTime } from "../discovery/notebook/relativeTime";
import { deriveTodaysFocus } from "../discovery/todaysFocus/deriveTodaysFocus";
import { useHistoryContext } from "../history/HistoryContext";
import { ALL_MODULES } from "../navigation/journeyConfig";

const TOTAL_CAREER_DNA_TRAITS = 10;

function timeOfDayGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

const QUICK_ACTIONS = [
  { label: "Career Explorer", to: "/explore/career-reality" },
  { label: "Decision Lab", to: "/decide/decision-lab" },
  { label: "College Explorer", to: "/experience/college-collaboration" },
  { label: "Journey", to: "/history" },
];

export function HomeScreen() {
  const { user } = useAuthContext();
  const {
    careerDna,
    hypotheses,
    notebookEntries,
    reflectionJournal,
    understandingStage,
    understandingNarrative,
  } = useDiscoveryContext();
  const { recentlyExplored } = useCareerExplorationContext();
  const { decisionMemory } = useDecisionContext();
  const { items: historyItems } = useHistoryContext();

  const todaysFocus = deriveTodaysFocus(hypotheses, careerDna);
  const topHypothesis = [...hypotheses].sort((a, b) => b.confidence - a.confidence)[0];
  const traitCount = Object.keys(careerDna).length;
  const displayName = (user?.user_metadata?.name as string | undefined) || user?.email || "there";
  const mostRecentMission = historyItems[0];

  const latestEntry = [...notebookEntries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )[0];
  const latestDecision = decisionMemory[0];
  const latestReflection = [...reflectionJournal]
    .filter((r) => r.response)
    .sort((a, b) => new Date(b.answered_at ?? 0).getTime() - new Date(a.answered_at ?? 0).getTime())[0];

  const hasRecentActivity = latestEntry || latestDecision || latestReflection || recentlyExplored.length > 0;
  const lockedModules = ALL_MODULES.filter((m) => m.locked);

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <p className="text-sm text-ink-faint">{timeOfDayGreeting()}, {displayName}.</p>
      <h1 className="mt-1 text-2xl font-light text-ink">
        What would you like to help Aureon understand today?
      </h1>
      <p className="mt-2 text-xs text-ink-faint">
        Career DNA: {traitCount}/{TOTAL_CAREER_DNA_TRAITS} traits recorded
      </p>

      <Link to="/discover/identity" className="mt-8 block">
        <Surface tone="raised" padding="lg" className="transition-colors hover:border-accent-soft/40">
          <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">{understandingStage}</p>
          <h2 className="mt-2 text-xl font-medium text-ink">Continue Current Mission</h2>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">{understandingNarrative}</p>
          <p className="mt-3 border-t border-border pt-3 text-xs leading-relaxed text-ink-faint">
            Today's focus: {todaysFocus}
          </p>
        </Surface>
      </Link>

      {mostRecentMission && (
        <Link to="/history" className="mt-4 block">
          <Surface tone="neutral" padding="sm" className="transition-colors hover:border-accent-soft/40">
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Most Recent Mission</p>
            <p className="mt-1 text-sm text-ink-muted">{mostRecentMission.mission_name}</p>
          </Surface>
        </Link>
      )}

      <div className="mt-6">
        <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Quick Actions</p>
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map((action) => (
            <Link
              key={action.to}
              to={action.to}
              className="rounded-full border border-border px-3.5 py-1.5 text-xs text-ink-muted transition-colors hover:border-accent-soft/40 hover:text-ink"
            >
              {action.label}
            </Link>
          ))}
        </div>
      </div>

      {topHypothesis && (
        <div className="mt-6">
          <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Current Hypothesis</p>
          <HypothesisCard hypothesis={topHypothesis} />
        </div>
      )}

      <div className="mt-10 border-t border-border pt-6">
        <p className="mb-3 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Recent Investigations</p>
        {!hasRecentActivity ? (
          <p className="text-sm text-ink-faint">Nothing yet — this builds as you explore.</p>
        ) : (
          <Field divided>
            {latestEntry && (
              <div className="py-3 first:pt-0">
                <p className="text-sm text-ink-muted">{latestEntry.text}</p>
                <p className="mt-1 font-mono text-[0.62rem] text-ink-faint">
                  {relativeTime(new Date(latestEntry.created_at).getTime())}
                </p>
              </div>
            )}
            {latestDecision && (
              <div className="py-3">
                <p className="text-sm text-ink-muted">{latestDecision.reason}</p>
                <p className="mt-1 font-mono text-[0.62rem] text-ink-faint">
                  {relativeTime(new Date(latestDecision.created_at).getTime())}
                </p>
              </div>
            )}
            {latestReflection && (
              <div className="py-3">
                <p className="text-sm text-ink-muted">{latestReflection.response}</p>
                <p className="mt-1 font-mono text-[0.62rem] text-ink-faint">Reflection</p>
              </div>
            )}
            {recentlyExplored.length > 0 && (
              <div className="flex flex-wrap gap-2 py-3 last:pb-0">
                {recentlyExplored.map((entry) => (
                  <Link
                    key={entry.careerId}
                    to={`/explore/career-reality/${entry.careerId}`}
                    className="rounded-full border border-border px-3 py-1.5 text-xs text-ink-muted transition-colors hover:border-accent-soft/30 hover:text-ink"
                  >
                    {entry.careerName}
                  </Link>
                ))}
              </div>
            )}
          </Field>
        )}
      </div>

      <div className="mt-10 border-t border-border pt-6">
        <p className="mb-3 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Ahead in your journey</p>
        <div className="flex flex-wrap gap-2">
          {lockedModules.map((module) => (
            <Link
              key={module.id}
              to={module.path}
              className="rounded-full border border-border px-3 py-1.5 text-xs text-ink-faint transition-colors hover:border-border-strong hover:text-ink-muted"
            >
              {module.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
