import { NavLink } from "react-router-dom";

import { cn } from "../../../design-system/cn";

export interface UniverseWorkspaceTab {
  id: string;
  label: string;
  path: string;
}

/**
 * Built from a plain data array rather than hardcoded JSX specifically
 * so a future Evidence tab (the student's orbiting-satellite evidence —
 * projects, certificates, resume, portfolio, research) can be added
 * later as a one-line config addition, without restructuring this
 * component. Discover Navigation Refactor: back to 4 tabs — Experience
 * Lab and Hidden Potential's merged Talent Discovery content now live
 * as their own top-level Discover destinations, not tabs here (see
 * features/navigation/journeyConfig.ts).
 */
export const UNIVERSE_WORKSPACE_TABS: UniverseWorkspaceTab[] = [
  { id: "overview", label: "Overview", path: "/discover/identity" },
  { id: "career-dna", label: "Career DNA", path: "/discover/career-dna" },
  { id: "hidden-potential", label: "Hidden Potential", path: "/discover/hidden-potential" },
  { id: "reflection-journal", label: "Reflection Journal", path: "/discover/reflection-journal" },
];

export function UniverseWorkspaceTabs() {
  return (
    <div className="flex gap-5 border-b border-border">
      {UNIVERSE_WORKSPACE_TABS.map((tab) => (
        <NavLink
          key={tab.id}
          to={tab.path}
          end
          className={({ isActive }) =>
            cn(
              "border-b-2 pb-2.5 text-sm transition-colors",
              isActive
                ? "border-accent-soft text-ink"
                : "border-transparent text-ink-muted hover:text-ink",
            )
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </div>
  );
}
