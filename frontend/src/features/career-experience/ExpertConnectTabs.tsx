import { NavLink } from "react-router-dom";

import { cn } from "../../design-system/cn";

export interface ExpertConnectTab {
  id: string;
  label: string;
  path: string;
}

/**
 * Connect restructuring — Expert Connect becomes the single human-
 * guidance hub; Mentorship and Parent Connect fold in here as tabs
 * instead of their own top-level nav destinations. Mirrors
 * discovery/components/UniverseWorkspaceTabs.tsx's pattern exactly:
 * each tab is a real route with its own screen, not client-only state.
 */
export const EXPERT_CONNECT_TABS: ExpertConnectTab[] = [
  { id: "find-experts", label: "Find Experts", path: "/experience/expert-connect" },
  { id: "my-mentors", label: "My Mentors", path: "/experience/expert-connect/my-mentors" },
  { id: "parent-connect", label: "Parent Connect", path: "/experience/expert-connect/parent-connect" },
];

export function ExpertConnectTabs() {
  return (
    <div className="flex gap-5 border-b border-border">
      {EXPERT_CONNECT_TABS.map((tab) => (
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
