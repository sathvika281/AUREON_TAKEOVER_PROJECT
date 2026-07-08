import { motion } from "framer-motion";
import { useState } from "react";
import type { FormEvent } from "react";

import { Surface } from "../../../design-system/components/Surface";
import { Button } from "../../../design-system/components/Button";
import { EASE_CALM } from "../../../design-system/motion";

/**
 * Reflection is not another chat message — its own dedicated surface.
 * Submitting still calls the same sendMessage() the free-text input
 * uses (the backend already tracks a reflection answer as "the
 * student's next message"); only the surface is dedicated, not the
 * underlying mechanism.
 */
export function ReflectionCard({
  prompt,
  onSubmit,
  disabled,
}: {
  prompt: string;
  onSubmit: (text: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || disabled) return;
    onSubmit(value);
    setValue("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: EASE_CALM }}
    >
      <Surface tone="raised" padding="md">
        <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Reflection</p>
        <p className="mt-1.5 text-sm italic leading-relaxed text-ink">{prompt}</p>
        <form onSubmit={handleSubmit} className="mt-3 space-y-2">
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            disabled={disabled}
            rows={3}
            placeholder="Write your reflection…"
            className="w-full resize-none rounded-lg border border-border bg-canvas/40 px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-accent/40 focus:outline-none disabled:opacity-50"
          />
          <Button type="submit" disabled={disabled || !value.trim()} size="md">
            Write Reflection
          </Button>
        </form>
      </Surface>
    </motion.div>
  );
}
