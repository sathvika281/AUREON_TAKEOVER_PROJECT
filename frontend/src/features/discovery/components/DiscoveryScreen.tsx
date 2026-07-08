import { AnimatePresence } from "framer-motion";

import { Badge } from "../../../design-system/components/Badge";
import { AureonMark } from "../../../design-system/components/Logo";
import { Surface } from "../../../design-system/components/Surface";
import { AgentActivityIndicator } from "../chat/AgentActivityIndicator";
import { CurrentQuestion } from "../chat/CurrentQuestion";
import { MessageBubble } from "../chat/MessageBubble";
import { MessageInput } from "../chat/MessageInput";
import { ReflectionCard } from "../chat/ReflectionCard";
import { useDiscoveryContext } from "../DiscoveryContext";
import { MissionCard } from "../exploration/MissionCard";
import { InvestigationsPanel } from "./InvestigationsPanel";
import { CareerDNAGraph } from "../network/CareerDNAGraph";
import { BeliefRevisionEntry } from "../notebook/BeliefRevisionEntry";
import { HypothesisCard } from "../notebook/HypothesisCard";
import { ObservationEntry } from "../notebook/ObservationEntry";
import { InsightMoment } from "../reveal/InsightMoment";
import { deriveTodaysFocus } from "../todaysFocus/deriveTodaysFocus";

/**
 * The Identity Discovery mission workspace. A mission header always
 * frames what's happening; conversation is one panel in the left column,
 * not the whole screen — evidence and findings live in their own column
 * on the right, always visible rather than buried below a chat thread.
 */
export function DiscoveryScreen() {
  const {
    messages,
    careerDna,
    hypotheses,
    notebookEntries,
    reflectionPrompt,
    suggestedActivity,
    confidenceScore,
    understandingStage,
    understandingNarrative,
    isSending,
    error,
    insightMomentLine,
    dismissInsightMoment,
    sendMessage,
  } = useDiscoveryContext();

  const todaysFocus = deriveTodaysFocus(hypotheses, careerDna);
  const orderedHypotheses = [...hypotheses].sort((a, b) => b.confidence - a.confidence);

  const lastAureonMessage = [...messages].reverse().find((m) => m.role === "aureon");

  const notebookPreview = [...notebookEntries]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 4);

  return (
    <div className="mx-auto max-w-5xl px-6 pb-16 pt-10">
      {/* Mission header */}
      <Surface tone="raised" padding="lg">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Mission</p>
        <h1 className="mt-1.5 text-xl font-medium text-ink">Identity Discovery</h1>
        <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{understandingNarrative}</p>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <Badge tone="warm">{understandingStage}</Badge>
          <Badge tone="neutral">Discovery</Badge>
        </div>
        <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-white/5">
          <div
            className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out"
            style={{ width: `${Math.round(confidenceScore * 100)}%` }}
          />
        </div>
      </Surface>

      <div className="mt-6 grid gap-6 lg:grid-cols-[3fr_2fr]">
        {/* Left: workspace */}
        <div className="space-y-6">
          <CareerDNAGraph careerDna={careerDna} isThinking={isSending} stillness={!!insightMomentLine} />

          <Surface tone="neutral" padding="md">
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Today's Focus</p>
            <p className="mt-1 text-sm leading-relaxed text-ink-muted">{todaysFocus}</p>
          </Surface>

          <div>
            {suggestedActivity ? (
              <MissionCard activity={suggestedActivity} />
            ) : reflectionPrompt ? (
              <ReflectionCard prompt={reflectionPrompt} onSubmit={sendMessage} disabled={isSending} />
            ) : lastAureonMessage ? (
              <CurrentQuestion text={lastAureonMessage.content} />
            ) : (
              <div className="flex flex-col items-center gap-3 py-2 text-center">
                <AureonMark size={32} />
                <p className="text-sm text-ink-faint">
                  Tell me what made you open Aureon today — there's no wrong answer.
                </p>
              </div>
            )}
          </div>

          <div>
            <div className="max-h-[18vh] space-y-3 overflow-y-auto rounded-xl border border-border bg-surface p-3">
              {messages.length === 0 && (
                <p className="text-center text-xs text-ink-faint">Your investigation will appear here.</p>
              )}
              {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
              ))}
              {isSending && <AgentActivityIndicator />}
            </div>
            {error && <p className="mt-2 text-center text-xs text-red-400">{error}</p>}
            <div className="mt-3">
              <MessageInput onSend={sendMessage} disabled={isSending} />
            </div>
          </div>
        </div>

        {/* Right: evidence & findings */}
        <div className="space-y-6">
          {notebookPreview.length > 0 && (
            <div>
              <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">
                Discovery Notebook
              </p>
              <Surface tone="neutral" padding="sm">
                <AnimatePresence>
                  {notebookPreview.map((entry) => (
                    <div key={entry.id}>
                      {entry.kind === "observation" ? (
                        <ObservationEntry entry={entry} />
                      ) : (
                        <BeliefRevisionEntry entry={entry} />
                      )}
                    </div>
                  ))}
                </AnimatePresence>
              </Surface>
            </div>
          )}

          {orderedHypotheses.length > 0 && (
            <div className="space-y-3">
              <p className="px-1 text-xs uppercase tracking-widest text-ink-faint">Working Hypotheses</p>
              <AnimatePresence mode="popLayout">
                {orderedHypotheses.map((hypothesis) => (
                  <HypothesisCard key={hypothesis.career_name} hypothesis={hypothesis} />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>

      <InvestigationsPanel />

      <InsightMoment line={insightMomentLine} onComplete={dismissInsightMoment} />
    </div>
  );
}
