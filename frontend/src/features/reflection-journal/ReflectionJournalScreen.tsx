import { Link } from "react-router-dom";
import { BookOpen, Lightbulb, MessageCircleQuestion, NotebookPen, Sprout } from "lucide-react";

import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { Surface } from "../../design-system/components/Surface";
import { UniverseSummaryCard } from "../discovery/components/UniverseSummaryCard";
import { UniverseWorkspaceTabs } from "../discovery/components/UniverseWorkspaceTabs";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { BeliefRevisionEntry } from "../discovery/notebook/BeliefRevisionEntry";
import { ObservationEntry } from "../discovery/notebook/ObservationEntry";
import { relativeTime } from "../discovery/notebook/relativeTime";

type FeedItem =
  | { kind: "notebook"; timestamp: number; key: string; render: JSX.Element }
  | { kind: "reflection"; timestamp: number; key: string; render: JSX.Element };

const WHY_IT_MATTERS_STEPS = [
  {
    icon: Lightbulb,
    title: "Reflection surfaces what conversation alone misses",
    description: "Some self-knowledge only shows up when you're asked to slow down and put it into words — this is where that happens.",
  },
  {
    icon: NotebookPen,
    title: "It becomes part of your record",
    description: "A written reflection joins the same Discovery Notebook as everything else Aureon observes — it doesn't disappear after the session.",
  },
  {
    icon: Sprout,
    title: "It can shape your Career DNA",
    description: "When a reflection gives Aureon something specific and evidenced, it's treated the same as anything said in conversation.",
  },
];

/**
 * The full Discovery Notebook history — not just the workspace's 2-3
 * entry preview — plus the Reflection Journal, merged into one
 * chronological feed. This is a long-term record now that it's
 * server-persisted, not a session transcript.
 */
export function ReflectionJournalScreen() {
  const {
    notebookEntries, reflectionJournal, reflectionPrompt, hypotheses, careerDna, confidenceScore, understandingStage,
    isLoading,
  } = useDiscoveryContext();

  const notebookItems: FeedItem[] = notebookEntries.map((entry) => ({
    kind: "notebook",
    timestamp: new Date(entry.created_at).getTime(),
    key: entry.id,
    render: entry.kind === "observation" ? <ObservationEntry entry={entry} /> : <BeliefRevisionEntry entry={entry} />,
  }));

  const reflectionItems: FeedItem[] = reflectionJournal
    .filter((r) => r.response && r.answered_at)
    .map((r, i) => ({
      kind: "reflection",
      timestamp: new Date(r.answered_at!).getTime(),
      key: `reflection-${i}-${r.answered_at}`,
      render: (
        <Surface tone="neutral" padding="md">
          <p className="text-xs italic text-ink-faint">{r.prompt}</p>
          <p className="mt-2 text-sm leading-relaxed text-ink">{r.response}</p>
          <p className="mt-2 text-[0.68rem] text-ink-faint">{relativeTime(new Date(r.answered_at!).getTime())}</p>
        </Surface>
      ),
    }));

  const feed = [...notebookItems, ...reflectionItems].sort((a, b) => b.timestamp - a.timestamp);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      {!isLoading && (
        <div className="mb-8 space-y-4">
          <UniverseSummaryCard
            hypotheses={hypotheses}
            careerDna={careerDna}
            confidenceScore={confidenceScore}
            understandingStage={understandingStage}
          />
          <UniverseWorkspaceTabs />
        </div>
      )}

      <h1 className="text-2xl font-light text-ink">Journey Journal</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Your evolving thoughts and everything Aureon has noticed — a running record, not a session log.
      </p>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : (
        <>
          {/* Why reflections matter */}
          <div className="mt-8">
            <ProcessSteps title="Why Reflection Matters" steps={WHY_IT_MATTERS_STEPS} />
          </div>

          {/* Current reflection prompt, if one is waiting */}
          {reflectionPrompt && (
            <div className="mt-6">
              <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Waiting for Your Reflection</p>
              <Surface tone="raised" padding="md">
                <div className="flex items-start gap-3">
                  <MessageCircleQuestion size={16} className="mt-0.5 shrink-0 text-accent-soft" />
                  <p className="text-sm leading-relaxed text-ink">{reflectionPrompt}</p>
                </div>
                <Link
                  to="/discover/identity"
                  className="mt-3 inline-block text-xs text-accent-soft transition-colors hover:text-accent"
                >
                  Answer this in Identity Discovery →
                </Link>
              </Surface>
            </div>
          )}

          {/* Timeline */}
          <div className="mt-8">
            <p className="mb-3 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Your Journal</p>
            {feed.length === 0 ? (
              <EmptyStatePanel
                icon={BookOpen}
                title="Your journal is empty"
                description="Reflections and notebook entries will appear here, newest first, once you've had a conversation with Aureon or answered a reflection prompt."
                action={
                  <Link
                    to="/discover/identity"
                    className="rounded-lg bg-accent px-4 py-2.5 text-sm font-medium tracking-wide text-ink transition-colors hover:bg-accent-soft"
                  >
                    Start a conversation
                  </Link>
                }
              />
            ) : (
              <div className="space-y-4">
                {feed.map((item) => (
                  <div key={item.key}>{item.render}</div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
