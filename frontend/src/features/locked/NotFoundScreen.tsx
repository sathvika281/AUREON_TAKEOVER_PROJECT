import { Compass } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";

/**
 * Sprint 7 — the global catch-all for any authenticated route Aureon has
 * no screen for. Lives inside AppShell's own <Routes> rather than the
 * outer router, so the sidebar/layout stays intact — this is "wrong
 * page," not "app is broken." Never shadows a known entity's own
 * specific not-found state (e.g. /projects/does-not-exist still resolves
 * ProjectDetailScreen and shows its own honest "Project not found" —
 * this route only matches paths with no matching pattern at all).
 */
export function NotFoundScreen() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <EmptyStatePanel
        icon={Compass}
        title="Page Not Found"
        description="This page doesn't exist, or may have moved."
        action={
          <Link to="/dashboard">
            <Button>Back to Mission Control</Button>
          </Link>
        }
      />
    </div>
  );
}
