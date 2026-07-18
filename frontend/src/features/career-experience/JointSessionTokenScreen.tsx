import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { apiClient } from "../../shared/api/client";
import type { SharedSessionAuthorRole, SharedSessionWithNotes } from "../../shared/api/types";

const ROLE_LABEL: Record<SharedSessionAuthorRole, string> = {
  student: "Student",
  participant: "Participant",
  expert: "Expert",
};

/**
 * The auth-free side of a Joint Session (internally `SharedSession`) —
 * reachable purely via its opaque `access_token`, with no login. This
 * is a parent, guardian, sibling, or counselor's only way in. Real
 * scheduling and shared notes only — no live video/calling.
 */
export function JointSessionTokenScreen() {
  const { token } = useParams<{ token: string }>();
  const [session, setSession] = useState<SharedSessionWithNotes | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const [participantLabel, setParticipantLabel] = useState("");
  const [authorRole, setAuthorRole] = useState<SharedSessionAuthorRole>("participant");
  const [noteText, setNoteText] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const load = () => {
    if (!token) return;
    setIsLoading(true);
    apiClient
      .get<SharedSessionWithNotes>(`/v1/shared-sessions/${token}`)
      .then(setSession)
      .catch(() => setNotFound(true))
      .finally(() => setIsLoading(false));
  };

  useEffect(load, [token]);

  if (isLoading) {
    return <div className="mx-auto max-w-xl px-6 py-16 text-sm text-ink-faint">Loading…</div>;
  }

  if (notFound || !session || !token) {
    return (
      <div className="mx-auto max-w-xl px-6 py-16">
        <h1 className="text-xl font-light text-ink">Session Not Found</h1>
        <p className="mt-2 text-sm text-ink-muted">
          This joint session link may have expired or been entered incorrectly.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-6 py-16">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Aureon · Joint Session</p>
      <h1 className="mt-2 text-2xl font-light text-ink">{session.topic}</h1>
      <p className="mt-1 text-xs text-ink-faint">
        Status: {session.status.replace(/_/g, " ")}
        {session.participant_label && ` · ${session.participant_label} has joined`}
      </p>

      {!session.participant_label && (
        <Surface tone="raised" padding="md" className="mt-6">
          <p className="mb-2 text-sm text-ink">Join this session</p>
          <p className="mb-3 text-xs text-ink-faint">
            Let the student know who's joining — for example "Mom", "Ms. Rodriguez (counselor)", or "older brother".
          </p>
          <Input
            value={participantLabel}
            onChange={(e) => setParticipantLabel(e.target.value)}
            placeholder="Your name or how you'd like to be identified"
          />
          <Button
            className="mt-3"
            disabled={!participantLabel.trim() || isBusy}
            onClick={async () => {
              setIsBusy(true);
              try {
                await apiClient.post(`/v1/shared-sessions/${token}/join`, { participant_label: participantLabel.trim() });
                load();
              } finally {
                setIsBusy(false);
              }
            }}
          >
            Join Session
          </Button>
        </Surface>
      )}

      <section className="mt-8">
        <p className="mb-2 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Shared Notes</p>
        {session.notes.length === 0 ? (
          <p className="text-xs text-ink-faint">No notes yet — the first note can be added below.</p>
        ) : (
          <div className="space-y-2">
            {session.notes.map((note) => (
              <Surface key={note.id} tone="raised" padding="sm">
                <p className="text-xs text-ink-faint">{ROLE_LABEL[note.author_role]}</p>
                <p className="mt-1 text-sm text-ink-muted">{note.note}</p>
              </Surface>
            ))}
          </div>
        )}

        <div className="mt-4 space-y-2">
          <select
            value={authorRole}
            onChange={(e) => setAuthorRole(e.target.value as SharedSessionAuthorRole)}
            className="w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink"
          >
            <option value="participant">I'm the participant (parent/guardian/etc.)</option>
            <option value="student">I'm the student</option>
            <option value="expert">I'm the expert</option>
          </select>
          <Input value={noteText} onChange={(e) => setNoteText(e.target.value)} placeholder="Add a shared note…" />
          <Button
            disabled={!noteText.trim() || isBusy}
            onClick={async () => {
              setIsBusy(true);
              try {
                await apiClient.post(`/v1/shared-sessions/${token}/notes`, { author_role: authorRole, note: noteText.trim() });
                setNoteText("");
                load();
              } finally {
                setIsBusy(false);
              }
            }}
          >
            Add Note
          </Button>
        </div>
      </section>
    </div>
  );
}
