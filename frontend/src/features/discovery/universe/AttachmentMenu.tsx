import { motion } from "framer-motion";

import { EASE_ARRIVE } from "../../../design-system/motion";
import { EVIDENCE_DOORS, type EvidenceType } from "./evidenceMissionCopy";

/**
 * The one attachment picker — anchored to the composer, not a full-app
 * modal takeover, closer to how ChatGPT/Claude/Apple Notes surface an
 * attachment picker right where you're typing. Nine real doors into
 * Aureon's one intelligence; none of them are named as separate AI
 * tools, and none are shown disabled — everything listed here already
 * routes to a real handler (see EvidenceMissionModal.tsx).
 */
export function AttachmentMenu({
  onChoose,
  onClose,
}: {
  onChoose: (type: EvidenceType) => void;
  onClose: () => void;
}) {
  return (
    <>
      {/* Transparent click-catcher — dismisses without dimming the
          screen, since this is a picker anchored to the input, not a
          separate destination. */}
      <div className="fixed inset-0 z-30" onClick={onClose} />

      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 8, scale: 0.98 }}
        transition={{ duration: 0.25, ease: EASE_ARRIVE }}
        className="absolute bottom-full left-0 z-40 mb-3 w-full max-w-sm origin-bottom-left rounded-2xl border border-[#2A2650]/70 bg-[#0C0A22]/95 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.5)] backdrop-blur-md"
      >
        <p className="font-serif text-base text-[#F2EDE0]">Help Aureon Understand You</p>
        <p className="mt-1 text-xs leading-relaxed text-[#6E6A5E]">
          Every project, document, link, and reflection you share becomes another part of your
          Universe.
        </p>

        <div className="mt-3 max-h-[60vh] overflow-y-auto">
          <div className="divide-y divide-[#2A2650]/70">
            {EVIDENCE_DOORS.map((door) => (
              <button
                key={door.type}
                onClick={() => onChoose(door.type)}
                className="flex w-full items-center gap-3 py-2.5 text-left transition-colors first:pt-0 last:pb-0 hover:text-[#F2EDE0]"
              >
                <door.icon size={16} className="shrink-0 text-[#D9B87A]" />
                <span>
                  <span className="block text-sm text-[#F2EDE0]">{door.label}</span>
                  <span className="block text-[0.7rem] text-[#6E6A5E]">{door.question}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      </motion.div>
    </>
  );
}
