import { motion } from "framer-motion";
import Markdown from "react-markdown";

import { DURATION, EASE_CALM, useReducedMotion } from "../../../design-system/motion";
import type { ChatMessage } from "../DiscoveryContext";
import { splitIntoSentences } from "./splitIntoSentences";

function RevealedMarkdown({ text }: { text: string }) {
  const reduced = useReducedMotion();
  const sentences = splitIntoSentences(text);

  return (
    <span className="prose-invert">
      {sentences.map((sentence, i) => (
        <motion.span
          key={i}
          className="inline"
          initial={reduced ? undefined : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: DURATION.settle, ease: EASE_CALM, delay: reduced ? 0 : i * 0.15 }}
        >
          <Markdown
            components={{
              p: ({ children }) => <span>{children} </span>,
            }}
          >
            {sentence}
          </Markdown>
        </motion.span>
      ))}
    </span>
  );
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isStudent = message.role === "student";

  return (
    <div className={`flex ${isStudent ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isStudent
            ? "max-w-[75%] rounded-xl bg-accent px-4 py-2.5 text-sm leading-relaxed text-ink"
            : "max-w-[75%] rounded-xl border border-border bg-surface px-5 py-3 text-[0.95rem] leading-loose text-ink"
        }
      >
        {isStudent ? message.content : <RevealedMarkdown text={message.content} />}
      </div>
    </div>
  );
}
