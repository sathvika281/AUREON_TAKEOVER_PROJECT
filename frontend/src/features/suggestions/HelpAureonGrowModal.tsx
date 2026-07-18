import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertCircle,
  BookOpen,
  Compass,
  Handshake,
  Lightbulb,
  type LucideIcon,
  MessageCircle,
  X,
} from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { EASE_CALM } from "../../design-system/motion";
import type { SuggestionCategory } from "../../shared/api/types";
import { useSuggestionsContext } from "./SuggestionsContext";

type Step = "category" | "form" | "success";

const CATEGORIES: { value: SuggestionCategory; label: string; hint: string; icon: LucideIcon }[] = [
  { value: "career", label: "Suggest a Career", hint: "“I couldn’t find Wildlife Photographer.”", icon: Compass },
  { value: "opportunity", label: "Suggest an Opportunity", hint: "A scholarship, fellowship, competition, grant…", icon: Handshake },
  { value: "resource", label: "Suggest a Resource", hint: "A book, podcast, community, journal…", icon: BookOpen },
  { value: "feature_request", label: "Request a Feature", hint: "“I wish Aureon could help me with…”", icon: Lightbulb },
  { value: "correction", label: "Report Incorrect or Outdated Info", hint: "“This scholarship deadline has changed.”", icon: AlertCircle },
  { value: "general_feedback", label: "General Feedback", hint: "“I found Career Explorer confusing because…”", icon: MessageCircle },
];

const SOURCE_URL_CATEGORIES: SuggestionCategory[] = ["opportunity", "resource", "correction"];

/**
 * "Help Aureon Grow" — opened globally from `JourneyNav`'s account-links
 * block, or pre-seeded via `openModal({...})` from a context-aware
 * trigger on a career/opportunity detail screen. Three steps: category
 * picker → dynamic form → confirmation. Structure copied from
 * `EvidenceMissionModal.tsx`'s fixed-overlay pattern, but with real
 * design tokens (`bg-canvas`, `border-border`) instead of that screen's
 * deliberate one-off hardcoded hex ritual palette.
 */
export function HelpAureonGrowModal() {
  const { isModalOpen, modalPrefill, closeModal, submitSuggestion, isBusy, error } = useSuggestionsContext();

  const [step, setStep] = useState<Step>("category");
  const [category, setCategory] = useState<SuggestionCategory | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [country, setCountry] = useState("");

  // This component stays mounted globally and toggles visibility rather
  // than mounting fresh per open, so state must be re-synced from
  // `modalPrefill` every time it opens — a `useState` initializer alone
  // would only ever run once, missing a second open with a different
  // context-aware prefill (e.g. opening from two different career
  // detail screens in the same session).
  useEffect(() => {
    if (!isModalOpen) return;
    setStep(modalPrefill?.category ? "form" : "category");
    setCategory(modalPrefill?.category ?? null);
    setTitle("");
    setDescription("");
    setSourceUrl("");
    setCountry("");
  }, [isModalOpen, modalPrefill]);

  if (!isModalOpen) return null;

  function handleClose() {
    closeModal();
  }

  function pickCategory(value: SuggestionCategory) {
    setCategory(value);
    setStep("form");
  }

  async function handleSubmit() {
    if (!category) return;
    const context_metadata = {
      ...(modalPrefill?.context_metadata ?? {}),
      ...(country.trim() ? { country: country.trim() } : {}),
    };
    const created = await submitSuggestion({
      category,
      title: title.trim(),
      description: description.trim(),
      source_url: sourceUrl.trim() || null,
      context_type: modalPrefill?.context_type ?? null,
      context_id: modalPrefill?.context_id ?? null,
      context_metadata: Object.keys(context_metadata).length > 0 ? context_metadata : null,
    });
    if (created) setStep("success");
  }

  const canSubmit = title.trim().length > 0 && description.trim().length > 0 && !isBusy;
  const activeCategory = CATEGORIES.find((c) => c.value === category);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4, ease: EASE_CALM }}
      className="fixed inset-0 z-40 flex items-center justify-center bg-canvas/95 px-6"
    >
      <div className="w-full max-w-md">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-ink">Help Aureon Grow</p>
            <p className="mt-0.5 text-xs text-ink-faint">You&rsquo;re helping improve Aureon for everyone.</p>
          </div>
          <button onClick={handleClose} className="text-ink-faint transition hover:text-ink">
            <X size={16} />
          </button>
        </div>

        {step === "category" && (
          <div className="mt-6 space-y-2">
            {CATEGORIES.map((c) => (
              <button
                key={c.value}
                onClick={() => pickCategory(c.value)}
                className="flex w-full items-start gap-3 rounded-xl border border-border bg-surface/70 px-4 py-3 text-left transition-colors duration-300 hover:border-accent-soft/50 hover:bg-surface"
              >
                <c.icon size={16} className="mt-0.5 shrink-0 text-accent-soft" />
                <div>
                  <p className="text-sm font-medium text-ink">{c.label}</p>
                  <p className="mt-0.5 text-xs text-ink-faint">{c.hint}</p>
                </div>
              </button>
            ))}
          </div>
        )}

        {step === "form" && activeCategory && (
          <div className="mt-6">
            <div className="flex items-center gap-2">
              <activeCategory.icon size={14} className="text-accent-soft" />
              <p className="text-xs uppercase tracking-widest text-ink-faint">{activeCategory.label}</p>
            </div>

            <div className="mt-4 space-y-3">
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title — e.g. “Wildlife Photographer”"
                maxLength={200}
              />
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Tell Aureon more…"
                rows={4}
                className="w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint transition-colors duration-300 focus:border-accent-soft/50 focus:bg-surface focus:outline-none"
              />
              {SOURCE_URL_CATEGORIES.includes(category!) && (
                <Input
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  placeholder="Link (optional)"
                  type="url"
                />
              )}
              {category === "opportunity" && (
                <Input
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  placeholder="Country (optional)"
                />
              )}
            </div>

            {error && <p className="mt-3 text-xs text-danger">{error}</p>}

            <div className="mt-5 flex gap-2">
              <Button className="flex-1" disabled={!canSubmit} onClick={handleSubmit}>
                {isBusy ? "Sending…" : "Send to Aureon"}
              </Button>
              {!modalPrefill?.category && (
                <Button variant="ghost" onClick={() => setStep("category")}>
                  Back
                </Button>
              )}
            </div>
          </div>
        )}

        {step === "success" && (
          <div className="mt-10 text-center">
            <p className="font-serif text-lg text-ink">Thank you — this helps everyone who comes after you.</p>
            <p className="mt-2 text-sm text-ink-muted">
              Aureon reviews every suggestion before it becomes part of the platform. You can track its
              status anytime.
            </p>
            <div className="mt-6 flex justify-center gap-2">
              <Link to="/suggestions" onClick={handleClose}>
                <Button>View My Suggestions</Button>
              </Link>
              <Button variant="ghost" onClick={handleClose}>
                Close
              </Button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
