import { motion } from "framer-motion";
import { useState } from "react";
import type { FormEvent } from "react";

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
      className="rounded-2xl border border-[#2A2650]/60 bg-[#0C0A22]/80 p-4 text-left shadow-[0_12px_36px_rgba(0,0,0,0.4)] backdrop-blur-md"
    >
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#D9B87A]">Reflection</p>
      <p className="mt-1.5 font-serif italic leading-relaxed text-[#F2EDE0]">{prompt}</p>
      <form onSubmit={handleSubmit} className="mt-3 space-y-2">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          rows={3}
          placeholder="Write your reflection…"
          className="w-full resize-none rounded-lg border border-[#3A3560] bg-[#070B18]/60 px-3 py-2 text-sm text-[#F2EDE0] placeholder:text-[#6E6A5E] focus:border-[#D9B87A]/40 focus:outline-none disabled:opacity-50"
        />
        <Button
          type="submit"
          disabled={disabled || !value.trim()}
          size="md"
          className="bg-[#D9B87A] text-[#141033] hover:bg-[#E9C98F]"
        >
          Write Reflection
        </Button>
      </form>
    </motion.div>
  );
}
