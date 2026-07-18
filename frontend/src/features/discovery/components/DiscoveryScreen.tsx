import { useDiscoveryContext } from "../DiscoveryContext";
import { CareerUniverse } from "../universe/CareerUniverse";
import { ConversationDock } from "../universe/ConversationDock";
import { CuriosityCheckIn } from "./CuriosityCheckIn";
import { OrbitStatus } from "./OrbitStatus";
import { UniverseSummaryCard } from "./UniverseSummaryCard";
import { UniverseWorkspaceTabs } from "./UniverseWorkspaceTabs";

/**
 * Your Universe (internal name: Identity Discovery) — rebuilt as an
 * interactive observatory, not a dashboard with a space theme. The
 * universe fills the whole screen and is the hero; every other element
 * (conversation, panels, status strip) is a quiet overlay living in its
 * negative space. Every visual is a re-rendering of data DiscoveryContext
 * already exposes — nothing here changes what Discovery computes, only
 * how it's shown. See features/discovery/universe/ for the visualization
 * itself. The workspace summary card + tab bar sit in their own chrome
 * strip above the scene, rather than overlaid on it, so they never
 * collide with the observatory's own top-left milestone rail.
 */
export function DiscoveryScreen() {
  const {
    messages,
    careerDna,
    hypotheses,
    notebookEntries,
    hiddenPotential,
    evidenceGraph,
    reflectionJournal,
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
    orbitStatus,
  } = useDiscoveryContext();

  return (
    <div className="flex h-full w-full flex-col">
      <div className="shrink-0 space-y-4 border-b border-border bg-canvas px-6 pb-4 pt-4">
        <UniverseSummaryCard
          hypotheses={hypotheses}
          careerDna={careerDna}
          confidenceScore={confidenceScore}
          understandingStage={understandingStage}
        />
        {orbitStatus && <OrbitStatus status={orbitStatus} />}
        <CuriosityCheckIn />
        <UniverseWorkspaceTabs />
      </div>

      <div className="relative min-h-0 flex-1">
        <CareerUniverse
          careerDna={careerDna}
          hypotheses={hypotheses}
          notebookEntries={notebookEntries}
          hiddenPotential={hiddenPotential}
          evidenceGraph={evidenceGraph}
          reflectionJournal={reflectionJournal}
          confidenceScore={confidenceScore}
          understandingStage={understandingStage}
          understandingNarrative={understandingNarrative}
          isThinking={isSending}
          insightMomentLine={insightMomentLine}
          onDismissInsightMoment={dismissInsightMoment}
        />

        <ConversationDock
          messages={messages}
          suggestedActivity={suggestedActivity}
          reflectionPrompt={reflectionPrompt}
          isSending={isSending}
          error={error}
          hasEvidence={notebookEntries.length > 0}
          onSend={sendMessage}
        />
      </div>
    </div>
  );
}
