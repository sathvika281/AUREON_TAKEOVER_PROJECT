import { useEffect, useState } from "react";
import { Link2, Users2 } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { useCareerExperienceContext } from "./CareerExperienceContext";

function joinLinkFor(token: string): string {
  return `${window.location.origin}/joint-session/${token}`;
}

const STATUS_LABEL: Record<string, string> = {
  invited: "Waiting for them to join",
  scheduled: "Scheduled",
  completed: "Completed",
  cancelled: "Cancelled",
};

/**
 * Student-side of a "Joint Session" (internally `SharedSession`) — pick
 * an expert and create a shareable invite link a parent, guardian,
 * sibling, or counselor can open without any login of their own. Real
 * scheduling only (no live video) — the shared notes thread happens on
 * the token-accessed screen this link opens.
 */
export function SharedSessionScreen() {
  const { experts, sharedSessions, isBusy, error, createSharedSessionInvite, isLoadingInitialData, ensureLoaded } =
    useCareerExperienceContext();
  const [selectedExpertId, setSelectedExpertId] = useState("");
  const [topic, setTopic] = useState("");
  const [lastCreatedToken, setLastCreatedToken] = useState<string | null>(null);

  useEffect(() => {
    ensureLoaded();
  }, [ensureLoaded]);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Joint Sessions</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Invite a parent, guardian, sibling, or counselor to join a real conversation with an
        expert alongside you — share the link below, no account needed on their end.
      </p>

      <Surface tone="raised" padding="md" className="mt-6">
        <p className="mb-3 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Create an Invite</p>

        <label className="block text-xs text-ink-faint">Expert</label>
        <select
          value={selectedExpertId}
          onChange={(e) => setSelectedExpertId(e.target.value)}
          className="mt-1 w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink"
        >
          <option value="">{isLoadingInitialData ? "Loading experts…" : "Choose an expert…"}</option>
          {experts.map((e) => (
            <option key={e.id} value={e.id}>{e.name}</option>
          ))}
        </select>

        <label className="mt-3 block text-xs text-ink-faint">Topic</label>
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="What would you like the three of you to discuss?"
          className="mt-1"
        />

        <Button
          className="mt-4"
          disabled={!selectedExpertId || !topic.trim() || isBusy}
          onClick={async () => {
            const session = await createSharedSessionInvite(selectedExpertId, null, topic.trim());
            if (session) {
              setLastCreatedToken(session.access_token);
              setTopic("");
              setSelectedExpertId("");
            }
          }}
        >
          Create Invite Link
        </Button>

        {error && <p className="mt-3 text-xs text-danger">{error}</p>}

        {lastCreatedToken && (
          <div className="mt-4 rounded-lg border border-accent-soft/30 bg-accent/5 p-3">
            <div className="flex items-center gap-1.5 text-accent-soft">
              <Link2 size={13} />
              <p className="text-xs">Share this link — it opens without any login</p>
            </div>
            <p className="mt-1 break-all font-mono text-xs text-ink-muted">{joinLinkFor(lastCreatedToken)}</p>
          </div>
        )}
      </Surface>

      <p className="mb-2 mt-10 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Your Joint Sessions</p>
      {isLoadingInitialData ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : sharedSessions.length === 0 ? (
        <EmptyStatePanel
          icon={Users2}
          title="No Joint Sessions Yet"
          description="Create an invite above to bring a parent, guardian, or mentor into a real conversation with an expert."
        />
      ) : (
        <div className="space-y-2">
          {sharedSessions.map((session) => (
            <Surface key={session.id} tone="raised" padding="sm">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-ink">{session.topic}</p>
                  <p className="mt-0.5 text-xs text-ink-faint">
                    {session.participant_label ? `With ${session.participant_label}` : "Waiting for a participant"}
                  </p>
                </div>
                <Badge tone={session.status === "completed" ? "success" : "cool"}>
                  {STATUS_LABEL[session.status] ?? session.status}
                </Badge>
              </div>
              <p className="mt-2 break-all font-mono text-[0.65rem] text-ink-faint">{joinLinkFor(session.access_token)}</p>
            </Surface>
          ))}
        </div>
      )}
    </div>
  );
}
