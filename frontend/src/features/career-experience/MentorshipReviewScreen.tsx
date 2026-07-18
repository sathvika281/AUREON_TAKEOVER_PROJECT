import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { Mentorship } from "../../shared/api/types";

/**
 * The expert's only way into a mentorship request — reachable purely
 * via its opaque `review_token`, with no login. Mirrors
 * `JointSessionTokenScreen.tsx` exactly: there is no expert-side
 * authentication anywhere in this system, so a `review_token` link is
 * the literal, deepest reuse of Joint Sessions' own architectural
 * answer to "a second party this system can't authenticate."
 */
export function MentorshipReviewScreen() {
  const { token } = useParams<{ token: string }>();
  const [mentorship, setMentorship] = useState<Mentorship | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const load = () => {
    if (!token) return;
    setIsLoading(true);
    apiClient
      .get<Mentorship>(`/v1/mentorship-review/${token}`)
      .then(setMentorship)
      .catch(() => setNotFound(true))
      .finally(() => setIsLoading(false));
  };

  useEffect(load, [token]);

  async function runAction(path: string, body?: unknown) {
    if (!token) return;
    setIsBusy(true);
    try {
      await apiClient.post(`/v1/mentorship-review/${token}${path}`, body ?? {});
      load();
    } finally {
      setIsBusy(false);
    }
  }

  if (isLoading) {
    return <div className="mx-auto max-w-xl px-6 py-16 text-sm text-ink-faint">Loading…</div>;
  }

  if (notFound || !mentorship || !token) {
    return (
      <div className="mx-auto max-w-xl px-6 py-16">
        <h1 className="text-xl font-light text-ink">Mentorship Request Not Found</h1>
        <p className="mt-2 text-sm text-ink-muted">
          This mentorship review link may have expired or been entered incorrectly.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-6 py-16">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Aureon · Mentorship Request</p>
      <div className="mt-2 flex items-center gap-2">
        <h1 className="text-2xl font-light text-ink">Mentorship Review</h1>
        <Badge tone={mentorship.status === "accepted" ? "warm" : mentorship.status === "completed" ? "success" : "neutral"}>
          {mentorship.status}
        </Badge>
      </div>

      {mentorship.goals && (
        <div className="mt-4">
          <p className="mb-1 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Student's Goals</p>
          <p className="text-sm leading-relaxed text-ink-muted">{mentorship.goals}</p>
        </div>
      )}

      {mentorship.status === "requested" && (
        <Surface tone="raised" padding="md" className="mt-6">
          <p className="mb-3 text-sm text-ink">A student has requested mentorship from you.</p>
          <div className="flex gap-2">
            <Button disabled={isBusy} onClick={() => runAction("/accept")}>
              Accept
            </Button>
            <Button variant="ghost" disabled={isBusy} onClick={() => runAction("/decline")}>
              Decline
            </Button>
          </div>
        </Surface>
      )}

      <section className="mt-8">
        <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Progress Notes</p>
        {mentorship.progress_notes.length === 0 ? (
          <p className="text-xs text-ink-faint">No notes yet.</p>
        ) : (
          <div className="space-y-2">
            {mentorship.progress_notes.map((note) => (
              <Surface key={note.id} tone="raised" padding="sm">
                <p className="text-xs text-ink-faint">{note.author_role === "student" ? "Student" : "You"}</p>
                <p className="mt-1 text-sm text-ink-muted">{note.note}</p>
              </Surface>
            ))}
          </div>
        )}

        {mentorship.status === "accepted" && (
          <div className="mt-4 space-y-2">
            <Input value={noteText} onChange={(e) => setNoteText(e.target.value)} placeholder="Add a progress note…" />
            <div className="flex gap-2">
              <Button
                disabled={!noteText.trim() || isBusy}
                onClick={async () => {
                  await runAction("/notes", { author_role: "expert", note: noteText.trim() });
                  setNoteText("");
                }}
              >
                Add Note
              </Button>
              <Button variant="ghost" disabled={isBusy} onClick={() => runAction("/complete")}>
                Mark Complete
              </Button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
