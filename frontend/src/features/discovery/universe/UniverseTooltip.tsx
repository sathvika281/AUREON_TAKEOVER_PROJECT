import type { UniverseExplanation } from "./explainUniverse";
import { LOW_EVIDENCE_FALLBACK } from "./explainUniverse";

/**
 * Shared hover/tap tooltip shell for the Moon and constellation lines —
 * copies Star.tsx's existing tooltip card styling verbatim so every
 * explanation surface in Your Universe reads as one consistent visual
 * language, not a new component design. Star.tsx keeps rendering its own
 * tooltip inline (already working, already tested); this is only for the
 * newly-interactive elements.
 */
export function UniverseTooltip({
  x,
  y,
  explanation,
}: {
  x: number;
  y: number;
  explanation: UniverseExplanation;
}) {
  const { title, subtitle, why, evidenceLine, isLowEvidence } = explanation;

  return (
    <foreignObject x={x} y={y} width={240} height={220} style={{ overflow: "visible" }}>
      <div className="pointer-events-none w-max max-w-[224px] rounded-lg border border-[#3A3560] bg-[#141033]/95 px-3 py-2 shadow-[0_8px_24px_rgba(0,0,0,0.5)] backdrop-blur-sm">
        <p className="text-xs font-medium text-[#F2EDE0]">{title}</p>
        {subtitle && (
          <p className="mt-0.5 font-mono text-[0.6rem] uppercase tracking-wide text-[#6E6A5E]">{subtitle}</p>
        )}

        {isLowEvidence ? (
          <p className="mt-1.5 text-[0.68rem] italic leading-relaxed text-[#6E6A5E]">{LOW_EVIDENCE_FALLBACK}</p>
        ) : (
          <>
            {why.length > 0 && (
              <div className="mt-1.5 space-y-0.5">
                {why.map((line, i) => (
                  <p key={i} className="text-[0.68rem] leading-relaxed text-[#9C978A]">
                    {line}
                  </p>
                ))}
              </div>
            )}
            {evidenceLine && (
              <p className="mt-1.5 font-mono text-[0.58rem] uppercase tracking-wide text-[#6E6A5E]">
                Based on: {evidenceLine}
              </p>
            )}
          </>
        )}
      </div>
    </foreignObject>
  );
}
