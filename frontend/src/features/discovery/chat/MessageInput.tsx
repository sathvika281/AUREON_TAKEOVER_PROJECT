import { ArrowUp, Paperclip } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { cn } from "../../../design-system/cn";

/**
 * One composer, ChatGPT/Claude-style — a single input with an inline
 * attachment button, never a separate "Investigations" surface. Typing
 * and attaching are two ways of doing the same thing: sharing something
 * with the one intelligence Aureon is.
 */
export function MessageInput({
  onSend,
  disabled,
  hasEvidence,
  onOpenAttachments,
  attachmentsOpen,
}: {
  onSend: (text: string) => void;
  disabled: boolean;
  hasEvidence: boolean;
  onOpenAttachments: () => void;
  attachmentsOpen: boolean;
}) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-1.5 rounded-2xl border border-[#2A2650]/70 bg-[#0C0A22]/75 py-1.5 pl-2 pr-2 shadow-[0_12px_36px_rgba(0,0,0,0.4)] backdrop-blur-md transition-colors focus-within:border-[#D9B87A]/40"
    >
      <button
        type="button"
        onClick={onOpenAttachments}
        aria-label={hasEvidence ? "Continue discovering your Universe" : "Share something about yourself"}
        aria-expanded={attachmentsOpen}
        className={cn(
          "relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-colors",
          attachmentsOpen ? "bg-[#D9B87A]/15 text-[#D9B87A]" : "text-[#6E6A5E] hover:bg-white/5 hover:text-[#9C978A]",
        )}
      >
        <Paperclip size={17} />
        {!hasEvidence && (
          <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-[#D9B87A]" aria-hidden="true" />
        )}
      </button>

      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
        placeholder={
          hasEvidence ? "Say what's on your mind…" : "Say what's on your mind, or attach something to share…"
        }
        className="min-w-0 flex-1 bg-transparent px-1.5 py-2 text-sm text-[#F2EDE0] placeholder:text-[#6E6A5E] focus:outline-none disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        aria-label="Send"
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#F2EDE0] text-[#141033] transition-colors hover:bg-[#D9B87A] disabled:cursor-not-allowed disabled:opacity-30"
      >
        <ArrowUp size={17} />
      </button>
    </form>
  );
}
