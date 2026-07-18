import { useCallback, useEffect, useState } from "react";

import { Badge } from "../../design-system/components/Badge";
import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { apiClient, ApiError } from "../../shared/api/client";
import type { SuggestionRecord, SuggestionsResponse, SuggestionStatus } from "../../shared/api/types";

const STATUS_OPTIONS: SuggestionStatus[] = [
  "pending",
  "under_review",
  "needs_information",
  "approved",
  "rejected",
  "implemented",
];

const STATUS_TONE: Record<SuggestionStatus, "neutral" | "warm" | "success" | "cool" | "gold"> = {
  pending: "cool",
  under_review: "warm",
  needs_information: "warm",
  approved: "gold",
  implemented: "success",
  rejected: "neutral",
};

function ReviewCard({
  suggestion,
  secret,
  onUpdated,
}: {
  suggestion: SuggestionRecord;
  secret: string;
  onUpdated: (updated: SuggestionRecord) => void;
}) {
  const [status, setStatus] = useState<SuggestionStatus>(suggestion.status);
  const [notes, setNotes] = useState(suggestion.review_notes ?? "");
  const [isSaving, setIsSaving] = useState(false);

  async function save() {
    setIsSaving(true);
    try {
      const updated = await apiClient.patch<SuggestionRecord>(
        `/v1/suggestions/${suggestion.id}/status`,
        { status, review_notes: notes.trim() || null },
        { "X-Aureon-Reviewer-Secret": secret },
      );
      onUpdated(updated);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Surface tone="raised" padding="md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-ink">{suggestion.title}</p>
          <p className="mt-0.5 text-xs text-ink-faint">
            {suggestion.category} · {suggestion.student_id}
          </p>
        </div>
        <Badge tone={STATUS_TONE[suggestion.status]}>{suggestion.status}</Badge>
      </div>
      <p className="mt-3 text-sm text-ink-muted">{suggestion.description}</p>
      {suggestion.source_url && (
        <a
          href={suggestion.source_url}
          target="_blank"
          rel="noreferrer"
          className="mt-2 inline-block text-xs text-accent-soft underline"
        >
          {suggestion.source_url}
        </a>
      )}
      {suggestion.context_type && (
        <p className="mt-1 text-xs text-ink-faint">
          From {suggestion.context_type}
          {suggestion.context_id ? ` (${suggestion.context_id})` : ""}
        </p>
      )}

      <div className="mt-4 space-y-2 border-t border-border pt-3">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as SuggestionStatus)}
          className="w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink focus:border-accent-soft/50 focus:bg-surface focus:outline-none"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Internal review notes…" />
        <Button size="md" disabled={isSaving} onClick={save}>
          {isSaving ? "Saving…" : "Save"}
        </Button>
      </div>
    </Surface>
  );
}

/**
 * The single reviewer screen for "Help Aureon Grow" submissions —
 * deliberately not linked from any nav (reachable only at
 * `/suggestions/review`, outside `AppShell`/`ProtectedRoute`, mirroring
 * `/mentorship-review/:token`). There is no admin/staff role anywhere in
 * this system to gate this behind instead; the reviewer secret entered
 * below is sent as `X-Aureon-Reviewer-Secret` on every request and
 * checked by `api/deps.py::require_reviewer_secret` — a normal student's
 * login grants zero access here.
 */
export function SuggestionReviewScreen() {
  const [secretInput, setSecretInput] = useState("");
  const [secret, setSecret] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<SuggestionRecord[]>([]);
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [q, setQ] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const load = useCallback(
    (activeSecret: string) => {
      setIsLoading(true);
      setAuthError(null);
      const params = new URLSearchParams();
      if (status) params.set("status", status);
      if (category) params.set("category", category);
      if (q) params.set("q", q);
      apiClient
        .get<SuggestionsResponse>(`/v1/suggestions?${params.toString()}`, {
          "X-Aureon-Reviewer-Secret": activeSecret,
        })
        .then((r) => setSuggestions(r.suggestions))
        .catch((err) => {
          if (err instanceof ApiError && err.status === 403) {
            setAuthError("Invalid reviewer secret.");
            setSecret(null);
          }
        })
        .finally(() => setIsLoading(false));
    },
    [status, category, q],
  );

  useEffect(() => {
    if (secret) load(secret);
  }, [secret, load]);

  if (!secret) {
    return (
      <div className="mx-auto max-w-sm px-6 py-24">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Aureon · Reviewer</p>
        <h1 className="mt-2 text-xl font-light text-ink">Suggestion Review</h1>
        <p className="mt-2 text-sm text-ink-muted">Enter the reviewer secret to continue.</p>
        <div className="mt-4 space-y-2">
          <Input
            type="password"
            value={secretInput}
            onChange={(e) => setSecretInput(e.target.value)}
            placeholder="Reviewer secret"
            onKeyDown={(e) => e.key === "Enter" && setSecret(secretInput)}
          />
          {authError && <p className="text-xs text-danger">{authError}</p>}
          <Button className="w-full" disabled={!secretInput.trim()} onClick={() => setSecret(secretInput)}>
            Continue
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Suggestion Review</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Every submission starts pending and never touches trusted data until you approve it here.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-lg border border-border bg-surface/70 px-3 py-2 text-sm text-ink focus:border-accent-soft/50 focus:outline-none"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-lg border border-border bg-surface/70 px-3 py-2 text-sm text-ink focus:border-accent-soft/50 focus:outline-none"
        >
          <option value="">All categories</option>
          <option value="career">career</option>
          <option value="opportunity">opportunity</option>
          <option value="resource">resource</option>
          <option value="feature_request">feature_request</option>
          <option value="correction">correction</option>
          <option value="general_feedback">general_feedback</option>
        </select>
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search title/description…"
          className="flex-1"
        />
      </div>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-faint">Loading…</p>
      ) : suggestions.length === 0 ? (
        <p className="mt-8 text-sm text-ink-faint">No suggestions match these filters.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {suggestions.map((s) => (
            <ReviewCard
              key={s.id}
              suggestion={s}
              secret={secret}
              onUpdated={(updated) =>
                setSuggestions((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
