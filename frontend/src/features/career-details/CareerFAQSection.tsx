import { Surface } from "../../design-system/components/Surface";
import type { CareerFAQ } from "../../shared/api/types";

/** Explore Polish Batch — honest myth-busting plus real, specific
 * student questions, never generic filler Q&A. */
export function CareerFAQSection({
  commonMisconceptions,
  faqs,
}: {
  commonMisconceptions: string[];
  faqs: CareerFAQ[];
}) {
  if (commonMisconceptions.length === 0 && faqs.length === 0) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      {commonMisconceptions.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Common misconceptions</p>
          <ul className="mt-1.5 space-y-1.5">
            {commonMisconceptions.map((item) => (
              <li key={item} className="flex gap-2 text-sm leading-relaxed text-ink-muted">
                <span className="text-ink-faint">✕</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {faqs.length > 0 && (
        <div>
          <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Frequently asked questions</p>
          <div className="mt-2 space-y-3">
            {faqs.map((faq) => (
              <div key={faq.question}>
                <p className="text-sm text-ink">{faq.question}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-ink-faint">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </Surface>
  );
}
