import { useState } from "react";

import type { Company } from "../../shared/api/types";

function initials(name: string): string {
  const words = name.split(/\s+/).filter(Boolean);
  return words.slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("");
}

/**
 * Real logo when it resolves; an honest initials-on-a-tile fallback when
 * it doesn't — never a broken-image icon. Genuinely new UI need this
 * sprint (Company is the first entity with real external images), kept
 * as its own small component since it's reused across the browse page,
 * detail page, and the Career page's Companies section — not a
 * speculative abstraction, a real one from the first use.
 */
export function CompanyLogo({ company, size = 40 }: { company: Company; size?: number }) {
  const [failed, setFailed] = useState(false);

  if (!company.logo_url || failed) {
    return (
      <div
        className="flex shrink-0 items-center justify-center rounded-lg border border-border bg-white/5 font-mono text-[0.65rem] text-ink-faint"
        style={{ width: size, height: size }}
      >
        {initials(company.name)}
      </div>
    );
  }

  return (
    <img
      src={company.logo_url}
      alt={`${company.name} logo`}
      onError={() => setFailed(true)}
      className="shrink-0 rounded-lg border border-border bg-white object-contain p-1.5"
      style={{ width: size, height: size }}
    />
  );
}
