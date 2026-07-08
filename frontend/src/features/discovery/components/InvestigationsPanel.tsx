import { useState } from "react";
import { FileText, GitBranch, Link2, Search } from "lucide-react";

import { cn } from "../../../design-system/cn";
import { DocumentIntelligenceScreen } from "../../document-intelligence/DocumentIntelligenceScreen";
import { GitHubIntelligenceScreen } from "../../github-intelligence/GitHubIntelligenceScreen";
import { SearchInvestigationScreen } from "../../search-investigation/SearchInvestigationScreen";
import { UrlInvestigationScreen } from "../../url-investigation/UrlInvestigationScreen";

type InvestigationTab = "github" | "document" | "url" | "search";

const TABS: { id: InvestigationTab; label: string; icon: typeof GitBranch }[] = [
  { id: "github", label: "GitHub", icon: GitBranch },
  { id: "document", label: "Documents", icon: FileText },
  { id: "url", label: "URL", icon: Link2 },
  { id: "search", label: "Search", icon: Search },
];

/**
 * GitHub/Document/URL/Search Intelligence all live inside Identity
 * Discovery — they're investigation tools that feed the same Career DNA/
 * Evidence Graph/Discovery Notebook this mission already builds, not
 * separate destinations. Each tab renders that feature's own existing
 * screen unmodified — only where it's mounted changed, not its logic.
 */
export function InvestigationsPanel() {
  const [tab, setTab] = useState<InvestigationTab>("github");

  return (
    <div className="mt-6">
      <p className="mb-2 px-1 text-xs uppercase tracking-widest text-ink-faint">
        Investigations
      </p>
      <div className="flex flex-wrap gap-2">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={cn(
              "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition",
              tab === id
                ? "border-accent/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:text-ink-muted",
            )}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      <div className="mt-4 rounded-2xl border border-border">
        {tab === "github" && <GitHubIntelligenceScreen />}
        {tab === "document" && <DocumentIntelligenceScreen />}
        {tab === "url" && <UrlInvestigationScreen />}
        {tab === "search" && <SearchInvestigationScreen />}
      </div>
    </div>
  );
}
