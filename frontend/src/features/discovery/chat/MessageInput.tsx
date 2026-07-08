import { ArrowUp } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

export function MessageInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-3">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
        placeholder="Say what's on your mind…"
        className="flex-1 rounded-full border border-border bg-surface px-5 py-3.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/50 focus:outline-none disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        aria-label="Send"
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-accent text-ink transition hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-30"
      >
        <ArrowUp size={18} />
      </button>
    </form>
  );
}
