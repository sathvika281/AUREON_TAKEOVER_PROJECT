import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { fadeInUp } from "../../design-system/motion";
import { apiClient } from "../../shared/api/client";
import type { OnboardingRequest, ProgressiveDiscoveryState } from "../../shared/api/types";
import { Layout } from "../../shared/components/Layout";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { getCurrentStudentId } from "../../shared/config/studentId";
import {
  CURRENT_SITUATIONS,
  LANGUAGES,
  STAGE_OPTIONS,
  WORLDS,
  type CurrentSituation,
  type StudentStage,
  type World,
} from "./onboardingConfig";

type Step = 1 | 2 | 3;
const TOTAL_STEPS = 3;

/**
 * Adaptive onboarding, trimmed to "just enough to personalize the first
 * session" — no per-world follow-up questions here; those are asked
 * gradually later by CuriosityCheckIn (features/discovery/components/).
 * Every choice with genuine uncertainty ("I have no idea," "I'm not
 * sure yet") is a first-class option, never a forced selection.
 */
export function OnboardingScreen() {
  const { user, completeOnboarding } = useAuthContext();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>(1);
  const [isSaving, setIsSaving] = useState(false);

  const [name, setName] = useState((user?.user_metadata?.name as string | undefined) ?? "");
  const [age, setAge] = useState("");
  const [stage, setStage] = useState<StudentStage | "">("");
  const [state, setState] = useState("");
  const [city, setCity] = useState("");
  const [language, setLanguage] = useState(LANGUAGES[0]);

  const [situation, setSituation] = useState<CurrentSituation | null>(null);

  const [selectedWorlds, setSelectedWorlds] = useState<World[]>([]);
  const [worldsUnsure, setWorldsUnsure] = useState(false);

  const canAdvanceFromStep1 =
    name.trim() !== "" && age.trim() !== "" && stage !== "" && state.trim() !== "" && city.trim() !== "";
  const canAdvanceFromStep2 = situation !== null;
  const canFinish = worldsUnsure || selectedWorlds.length > 0;

  const toggleWorld = (world: World) => {
    setWorldsUnsure(false);
    setSelectedWorlds((prev) => (prev.includes(world) ? prev.filter((w) => w !== world) : [...prev, world]));
  };

  const selectUnsure = () => {
    setSelectedWorlds([]);
    setWorldsUnsure((prev) => !prev);
  };

  const finish = async () => {
    if (!canFinish || isSaving) return;
    setIsSaving(true);

    // The real save — Discover Batch 1's backend migration Profile
    // Service owns this now. AuthContext's completeOnboarding stays only
    // as the fast, synchronous client-side gate mirror OnboardingGate
    // already reads (no network latency added to that check).
    const request: OnboardingRequest = {
      name: name || null,
      age: age ? Number(age) : null,
      stage: stage || null,
      location_state: state || null,
      location_city: city || null,
      preferred_language: language,
      current_situation: situation,
      worlds: selectedWorlds,
      worlds_unsure: worldsUnsure,
    };
    await apiClient.post<ProgressiveDiscoveryState>(
      `/v1/students/${getCurrentStudentId()}/onboarding`,
      request,
    );
    // Sprint 11 — name continuity fix: the onboarding form pre-fills from
    // (and lets a student correct) whatever name signup collected, but
    // previously only the backend's own onboarding record heard the
    // update. user_metadata.name is the one representation Mission
    // Control and Profile actually display, so it has to hear it too —
    // same completeOnboarding()/updateUser() merge Sprint 10's Profile
    // name edit already uses, not a second name store.
    await completeOnboarding({ onboarding_completed: true, name });

    setIsSaving(false);
    navigate("/dashboard");
  };

  return (
    <Layout>
      <div className="flex h-full items-center justify-center px-6 py-10">
        <div className="w-full max-w-lg">
          <p className="text-center font-mono text-[0.65rem] uppercase tracking-[0.14em] text-ink-faint">
            Step {step} of {TOTAL_STEPS}
          </p>

          <Surface tone="raised" padding="lg" className="mt-4">
            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div key="step-1" {...fadeInUp}>
                  <h2 className="text-lg font-medium text-ink">A little about you</h2>
                  <p className="mt-1 text-sm text-ink-muted">
                    Just enough for Aureon to personalize your first session.
                  </p>
                  <div className="mt-5 space-y-3">
                    <Input placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
                    <Input
                      type="number"
                      placeholder="Age"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      min={1}
                    />
                    <div className="flex gap-2">
                      {STAGE_OPTIONS.map((option) => (
                        <button
                          key={option}
                          type="button"
                          onClick={() => setStage(option)}
                          className={cn(
                            "flex-1 rounded-full border px-3 py-1.5 text-xs transition-colors",
                            stage === option
                              ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                              : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
                          )}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                    <div className="flex gap-3">
                      <Input placeholder="State" value={state} onChange={(e) => setState(e.target.value)} />
                      <Input placeholder="District / City" value={city} onChange={(e) => setCity(e.target.value)} />
                    </div>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface/70 px-4 py-2.5 text-sm text-ink transition-colors duration-300 focus:border-accent-soft/50 focus:bg-surface focus:outline-none"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang} value={lang}>
                          {lang}
                        </option>
                      ))}
                    </select>
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div key="step-2" {...fadeInUp}>
                  <h2 className="text-lg font-medium text-ink">Where are you right now?</h2>
                  <p className="mt-1 text-sm text-ink-muted">
                    There's no wrong answer here — uncertainty is completely valid.
                  </p>
                  <div className="mt-5 space-y-2">
                    {CURRENT_SITUATIONS.map((option) => (
                      <button
                        key={option.id}
                        type="button"
                        onClick={() => setSituation(option.id)}
                        className={cn(
                          "block w-full rounded-lg border px-4 py-2.5 text-left text-sm transition-colors",
                          situation === option.id
                            ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                            : "border-border text-ink-muted hover:border-border-strong hover:text-ink",
                        )}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div key="step-3" {...fadeInUp}>
                  <h2 className="text-lg font-medium text-ink">Worlds you're curious about</h2>
                  <p className="mt-1 text-sm text-ink-muted">
                    Pick as many as you like — or tell Aureon you're not sure yet, which is just as valuable.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {WORLDS.map((world) => (
                      <button
                        key={world}
                        type="button"
                        onClick={() => toggleWorld(world)}
                        className={cn(
                          "rounded-full border px-3.5 py-1.5 text-sm transition-colors",
                          selectedWorlds.includes(world)
                            ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                            : "border-border text-ink-muted hover:border-border-strong hover:text-ink",
                        )}
                      >
                        {world}
                      </button>
                    ))}
                    <button
                      type="button"
                      onClick={selectUnsure}
                      className={cn(
                        "rounded-full border px-3.5 py-1.5 text-sm transition-colors",
                        worldsUnsure
                          ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                          : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
                      )}
                    >
                      I'm not sure yet
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="mt-6 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStep((s) => (s > 1 ? ((s - 1) as Step) : s))}
                disabled={step === 1}
                className="text-xs text-ink-faint transition-colors hover:text-ink-muted disabled:cursor-not-allowed disabled:opacity-0"
              >
                Back
              </button>

              {step < 3 ? (
                <Button
                  onClick={() => setStep((s) => (s + 1) as Step)}
                  disabled={step === 1 ? !canAdvanceFromStep1 : !canAdvanceFromStep2}
                >
                  Continue
                </Button>
              ) : (
                <Button onClick={finish} disabled={!canFinish || isSaving}>
                  {isSaving ? "Please wait…" : "Finish"}
                </Button>
              )}
            </div>
          </Surface>
        </div>
      </div>
    </Layout>
  );
}
