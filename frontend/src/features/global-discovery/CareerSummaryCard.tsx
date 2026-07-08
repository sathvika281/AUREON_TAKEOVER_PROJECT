import { Link } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Surface } from "../../design-system/components/Surface";
import type { CareerSummary } from "../../shared/api/types";

export function CareerSummaryCard({ career }: { career: CareerSummary }) {
  return (
    <Link to={`/explore/career-reality/${career.id}`}>
      <Surface tone="neutral" padding="md" className="h-full transition hover:border-accent/30">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium text-ink">{career.name}</p>
          <Badge tone="cool">{career.category.replace("_", " ")}</Badge>
        </div>
        <p className="mt-2 text-xs leading-relaxed text-ink-muted">{career.one_liner}</p>
        {career.countries.length > 0 && (
          <p className="mt-2 text-[0.68rem] text-ink-faint">{career.countries.join(", ")}</p>
        )}
      </Surface>
    </Link>
  );
}
