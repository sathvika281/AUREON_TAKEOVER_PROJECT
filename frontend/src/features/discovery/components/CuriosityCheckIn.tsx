import { useState } from "react";

import { Surface } from "../../../design-system/components/Surface";
import { useDiscoveryContext } from "../DiscoveryContext";

/**
 * "Continuous onboarding" — Aureon learning gradually, one small
 * question at a time, rather than a Day-1 interrogation. Renders
 * nothing when there's no genuinely pending world (never an empty
 * placeholder card), and dismissing is a real, honored answer — "ask me
 * later" hides it for this session only, it never nags again within one
 * visit, and it never marks the world as answered. Purely
 * presentational — the pending world and its question content are real
 * backend-computed state (Progressive Discovery Service).
 */
export function CuriosityCheckIn() {
  const { pendingCuriosityCheckin, answerCuriosityCheckIn } = useDiscoveryContext();
  const [dismissedWorld, setDismissedWorld] = useState<string | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  if (!pendingCuriosityCheckin || pendingCuriosityCheckin.world === dismissedWorld) return null;
  const { world, prompt, options } = pendingCuriosityCheckin;

  const toggleOption = (option: string) => {
    setSelected((prev) => (prev.includes(option) ? prev.filter((o) => o !== option) : [...prev, option]));
  };

  const answer = async () => {
    if (selected.length === 0 || isSaving) return;
    setIsSaving(true);
    await answerCuriosityCheckIn(world, selected);
    setSelected([]);
    setIsSaving(false);
  };

  return (
    <Surface tone="neutral" padding="sm">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-accent-soft">Curiosity Check-in</p>
      <p className="mt-1.5 text-sm font-medium text-ink">
        You mentioned {world} interests you. {prompt}
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => toggleOption(option)}
            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
              selected.includes(option)
                ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-4">
        <button
          type="button"
          onClick={answer}
          disabled={selected.length === 0 || isSaving}
          className="text-xs font-medium text-accent-soft transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isSaving ? "Saving…" : "Answer"}
        </button>
        <button
          type="button"
          onClick={() => setDismissedWorld(world)}
          className="text-xs text-ink-faint transition-colors hover:text-ink-muted"
        >
          Ask me later
        </button>
      </div>
    </Surface>
  );
}
