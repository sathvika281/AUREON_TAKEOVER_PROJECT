import { AnimatePresence } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";

import type { ChatMessage } from "../DiscoveryContext";
import type { SuggestedActivity } from "../../../shared/api/types";
import { AgentActivityIndicator } from "../chat/AgentActivityIndicator";
import { CurrentQuestion } from "../chat/CurrentQuestion";
import { MessageInput } from "../chat/MessageInput";
import { ReflectionCard } from "../chat/ReflectionCard";
import { MissionCard } from "../exploration/MissionCard";
import { AttachmentMenu } from "./AttachmentMenu";
import { EvidenceMissionModal } from "./EvidenceMissionModal";
import type { EvidenceType } from "./evidenceMissionCopy";
import { UniverseIntro } from "./UniverseIntro";

/**
 * The conversation is secondary to the universe — never a persistent
 * message log competing with the Moon. Aureon's latest question floats
 * quietly above a slim, pinned composer; the rest of the conversation
 * lives in Journey Journal, one link away. Aureon has one intelligence,
 * not four separate tools — a single composer with an inline attachment
 * button (MessageInput -> AttachmentMenu -> EvidenceMissionModal) is the
 * only way in, exactly like attaching a file in ChatGPT/Claude rather
 * than picking between AI utilities.
 */
export function ConversationDock({
  messages,
  suggestedActivity,
  reflectionPrompt,
  isSending,
  error,
  hasEvidence,
  onSend,
}: {
  messages: ChatMessage[];
  suggestedActivity: SuggestedActivity | null;
  reflectionPrompt: string | null;
  isSending: boolean;
  error: string | null;
  hasEvidence: boolean;
  onSend: (text: string) => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeDoor, setActiveDoor] = useState<EvidenceType | null>(null);
  const lastAureonMessage = [...messages].reverse().find((m) => m.role === "aureon");

  return (
    <>
      <div className="pointer-events-none absolute inset-x-6 bottom-40 mx-auto max-w-md text-center md:inset-x-auto md:left-1/2 md:-translate-x-1/2">
        {messages.length === 0 ? (
          <UniverseIntro />
        ) : suggestedActivity ? (
          <MissionCard activity={suggestedActivity} />
        ) : reflectionPrompt ? (
          <div className="pointer-events-auto">
            <ReflectionCard prompt={reflectionPrompt} onSubmit={onSend} disabled={isSending} />
          </div>
        ) : lastAureonMessage ? (
          <CurrentQuestion text={lastAureonMessage.content} />
        ) : null}

        {isSending && (
          <div className="mt-3">
            <AgentActivityIndicator />
          </div>
        )}
        {error && <p className="mt-2 text-xs text-danger">{error}</p>}
      </div>

      <div className="absolute inset-x-6 bottom-14 mx-auto max-w-xl md:left-1/2 md:right-auto md:w-full md:-translate-x-1/2">
        <div className="relative">
          <MessageInput
            onSend={onSend}
            disabled={isSending}
            hasEvidence={hasEvidence}
            attachmentsOpen={menuOpen}
            onOpenAttachments={() => setMenuOpen((open) => !open)}
          />

          <AnimatePresence>
            {menuOpen && (
              <AttachmentMenu
                onClose={() => setMenuOpen(false)}
                onChoose={(type) => {
                  setMenuOpen(false);
                  setActiveDoor(type);
                }}
              />
            )}
          </AnimatePresence>
        </div>

        {messages.length > 0 && (
          <Link
            to="/discover/reflection-journal"
            className="mt-1.5 block text-right font-mono text-[0.62rem] uppercase tracking-wide text-[#6E6A5E] transition-colors hover:text-[#9C978A]"
          >
            View full conversation →
          </Link>
        )}
      </div>

      <AnimatePresence>
        {activeDoor && <EvidenceMissionModal evidenceType={activeDoor} onClose={() => setActiveDoor(null)} />}
      </AnimatePresence>
    </>
  );
}
