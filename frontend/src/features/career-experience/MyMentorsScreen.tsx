import { useState } from "react";
import { Handshake } from "lucide-react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import type { Mentorship } from "../../shared/api/types";
import { useCareerExperienceContext } from "./CareerExperienceContext";
import { ExpertConnectTabs } from "./ExpertConnectTabs";

function MentorshipCard({ mentorship }: { mentorship: Mentorship }) {
  const { addMentorshipNote, completeMentorship, isBusy } = useCareerExperienceContext();
  const [noteText, setNoteText] = useState("");
  const displayName = mentorship.expert_name || `Expert ${mentorship.expert_id}`;

  return (
    <Surface tone="raised" padding="md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-ink">{displayName}</p>
          {(mentorship.expert_role || mentorship.expert_domain) && (
            <p className="mt-0.5 text-xs text-ink-faint">
              {[mentorship.expert_role, mentorship.expert_domain].filter(Boolean).join(" · ")}
            </p>
          )}
          {mentorship.goals && <p className="mt-1 text-xs text-ink-muted">{mentorship.goals}</p>}
        </div>
      </div>

      {mentorship.progress_notes.length > 0 && (
        <div className="mt-4 space-y-2 border-t border-border pt-3">
          {mentorship.progress_notes.map((note) => (
            <div key={note.id}>
              <p className="text-xs text-ink-faint">{note.author_role === "expert" ? "Expert" : "You"}</p>
              <p className="text-sm text-ink-muted">{note.note}</p>
            </div>
          ))}
        </div>
      )}

      {mentorship.status === "accepted" && (
        <div className="mt-4 space-y-2">
          <Input
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Add a progress note…"
          />
          <div className="flex gap-2">
            <Button
              size="md"
              disabled={!noteText.trim() || isBusy}
              onClick={async () => {
                await addMentorshipNote(mentorship.id, "student", noteText.trim());
                setNoteText("");
              }}
            >
              Add Note
            </Button>
            <Button
              variant="ghost"
              size="md"
              disabled={isBusy}
              onClick={() => completeMentorship(mentorship.id)}
            >
              Mark Complete
            </Button>
          </div>
        </div>
      )}
    </Surface>
  );
}

function MentorshipSection({
  title,
  badgeTone,
  mentorships,
}: {
  title: string;
  badgeTone: "cool" | "warm" | "success" | "neutral";
  mentorships: Mentorship[];
}) {
  if (mentorships.length === 0) return null;
  return (
    <section className="mt-8">
      <div className="mb-3 flex items-center gap-2 px-1">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">{title}</p>
        <Badge tone={badgeTone}>{mentorships.length}</Badge>
      </div>
      <div className="space-y-3">
        {mentorships.map((m) => (
          <MentorshipCard key={m.id} mentorship={m} />
        ))}
      </div>
    </section>
  );
}

/**
 * My Mentors (Connect restructuring) — the tab Mentorship folded into
 * inside Expert Connect, no longer a separate top-level destination.
 * Requesting still happens from an expert's own detail view (Show
 * More → Request as Mentor); this tab is purely the student's own
 * relationships, now grouped by real status with resolved expert
 * identity (see api/v1/mentorship.py's expert_name/role/domain
 * enrichment) instead of a raw expert_id.
 */
export function MyMentorsScreen() {
  const { mentorships } = useCareerExperienceContext();

  const pending = mentorships.filter((m) => m.status === "requested");
  const accepted = mentorships.filter((m) => m.status === "accepted");
  const completed = mentorships.filter((m) => m.status === "completed");
  const declined = mentorships.filter((m) => m.status === "declined");

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <ExpertConnectTabs />
      <h1 className="mt-6 text-2xl font-light text-ink">My Mentors</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Your real mentorship requests and relationships. Request mentorship from an expert's profile
        under Find Experts — the expert reviews and accepts or declines from their own secure link,
        since there's no expert login in this system.
      </p>

      {mentorships.length === 0 ? (
        <div className="mt-8">
          <EmptyStatePanel
            icon={Handshake}
            title="No Mentors Yet"
            description="Visit an expert's profile under Find Experts and request them as a mentor if they're accepting mentees."
          />
        </div>
      ) : (
        <>
          <MentorshipSection title="Pending — Waiting for Mentor" badgeTone="cool" mentorships={pending} />
          <MentorshipSection title="Accepted — Your Mentors" badgeTone="warm" mentorships={accepted} />
          <MentorshipSection title="Completed" badgeTone="success" mentorships={completed} />
          <MentorshipSection title="Declined" badgeTone="neutral" mentorships={declined} />
        </>
      )}
    </div>
  );
}
