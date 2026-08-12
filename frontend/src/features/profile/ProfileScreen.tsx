import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Surface } from "../../design-system/components/Surface";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { useHistoryContext } from "../history/HistoryContext";

const TOTAL_CAREER_DNA_TRAITS = 10;
const MIN_PASSWORD_LENGTH = 6;

type SaveStatus = "idle" | "saving" | "success" | "error";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

/** Transient "Saved"/"Updated" confirmations clear themselves after a
 * few seconds rather than lingering as stale state. */
function useAutoClearSuccess(status: SaveStatus, setStatus: (s: SaveStatus) => void) {
  useEffect(() => {
    if (status !== "success") return;
    const timeout = setTimeout(() => setStatus("idle"), 3000);
    return () => clearTimeout(timeout);
  }, [status, setStatus]);
}

/** Profile — "The Identity Archive." */
export function ProfileScreen() {
  const { user, signOut, completeOnboarding, updatePassword } = useAuthContext();
  const { careerDna } = useDiscoveryContext();
  const { items } = useHistoryContext();
  const navigate = useNavigate();

  const name = (user?.user_metadata?.name as string | undefined) || null;
  const traitCount = Object.keys(careerDna).length;
  const latestInvestigation = items.find((i) => i.mission_type === "search_investigation");
  const latestSimulation = items.find((i) => i.mission_type === "career_simulation");

  const handleSignOut = async () => {
    await signOut();
    navigate("/login");
  };

  // --- Name edit — the one profile field with a real, already-persisted,
  // round-trip backend representation (Supabase Auth user_metadata, the
  // same store the onboarding wizard's own name field already writes
  // to). Other onboarding-collected fields (age, location, etc.) are
  // write-only from the frontend's perspective today — no existing GET
  // route echoes them back, so they're deliberately not made editable
  // here. ---
  const [isEditingName, setIsEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState("");
  const [nameStatus, setNameStatus] = useState<SaveStatus>("idle");
  const [nameError, setNameError] = useState<string | null>(null);
  useAutoClearSuccess(nameStatus, setNameStatus);

  const startEditingName = () => {
    setNameDraft(name ?? "");
    setNameError(null);
    setNameStatus("idle");
    setIsEditingName(true);
  };

  const cancelEditingName = () => {
    setIsEditingName(false);
    setNameError(null);
    setNameStatus("idle");
  };

  const saveName = async () => {
    const trimmed = nameDraft.trim();
    if (!trimmed) {
      setNameError("Name can't be empty.");
      return;
    }
    setNameError(null);
    setNameStatus("saving");
    const result = await completeOnboarding({ name: trimmed });
    if (result.error) {
      setNameStatus("error");
      setNameError(result.error);
      return;
    }
    setNameStatus("success");
    setIsEditingName(false);
  };

  // --- Change Password — reuses Sprint 6's updatePassword(), the same
  // supabase.auth.updateUser({password}) call ResetPasswordScreen uses.
  // Confirmed to work from a normal authenticated session (not only a
  // recovery session). Supabase does not invalidate the current session
  // on a plain password change, so — unlike the post-recovery flow —
  // the student stays signed in here; that's Supabase's real behavior,
  // not a weakened security posture. ---
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordStatus, setPasswordStatus] = useState<SaveStatus>("idle");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  useAutoClearSuccess(passwordStatus, setPasswordStatus);

  const passwordsMatch = newPassword === confirmPassword;
  const isLongEnough = newPassword.trim().length >= MIN_PASSWORD_LENGTH;
  const canSubmitPassword = isLongEnough && passwordsMatch && passwordStatus !== "saving";

  const startChangingPassword = () => {
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError(null);
    setPasswordStatus("idle");
    setIsChangingPassword(true);
  };

  const cancelChangingPassword = () => {
    setIsChangingPassword(false);
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError(null);
    setPasswordStatus("idle");
  };

  const submitPasswordChange = async () => {
    if (!canSubmitPassword) return;
    setPasswordStatus("saving");
    setPasswordError(null);
    const result = await updatePassword(newPassword);
    if (result.error) {
      setPasswordStatus("error");
      setPasswordError(result.error);
      return;
    }
    setNewPassword("");
    setConfirmPassword("");
    setIsChangingPassword(false);
    setPasswordStatus("success");
  };

  return (
    <div className="mx-auto max-w-xl px-6 py-10">
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.16em] text-accent-soft">
        The Identity Archive
      </p>
      <h1 className="mt-2 text-2xl font-light text-ink">Profile</h1>

      <Surface tone="raised" padding="md" className="mt-8">
        <div className="space-y-2 text-sm">
          {isEditingName ? (
            <div className="space-y-2">
              <Input
                value={nameDraft}
                onChange={(e) => setNameDraft(e.target.value)}
                placeholder="Full name"
                autoComplete="name"
                autoFocus
              />
              {nameError && <p className="text-xs text-danger">{nameError}</p>}
              <div className="flex gap-2">
                <Button size="md" onClick={saveName} disabled={nameStatus === "saving"}>
                  {nameStatus === "saving" ? "Saving…" : "Save"}
                </Button>
                <Button variant="ghost" onClick={cancelEditingName} disabled={nameStatus === "saving"}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <p className="flex flex-wrap items-center gap-2">
              <span className="text-ink-faint">Name: </span>
              <span className="text-ink">{name ?? "Not set"}</span>
              <button
                type="button"
                onClick={startEditingName}
                className="text-xs text-accent-soft transition-colors hover:underline"
              >
                Edit
              </button>
              {nameStatus === "success" && <span className="text-xs text-accent-soft">Saved</span>}
            </p>
          )}
          <p><span className="text-ink-faint">Email: </span><span className="text-ink">{user?.email}</span></p>
          {user?.created_at && (
            <p><span className="text-ink-faint">Member since: </span><span className="text-ink">{formatDate(user.created_at)}</span></p>
          )}
        </div>
      </Surface>

      <Surface tone="neutral" padding="md" className="mt-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Career DNA Completion</p>
            <p className="mt-1 text-ink">{traitCount}/{TOTAL_CAREER_DNA_TRAITS} traits</p>
          </div>
          <div>
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Total Missions</p>
            <p className="mt-1 text-ink">{items.length}</p>
          </div>
          <div>
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Latest Investigation</p>
            <p className="mt-1 text-ink-muted">{latestInvestigation?.mission_name ?? "None yet"}</p>
          </div>
          <div>
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Latest Simulation</p>
            <p className="mt-1 text-ink-muted">{latestSimulation?.mission_name ?? "None yet"}</p>
          </div>
          <div>
            <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Latest Progress Report</p>
            <p className="mt-1 text-ink-muted">
              Progress is always computed live —{" "}
              <a href="/build/progress-intelligence" className="text-accent-soft hover:underline">view current report</a>.
            </p>
          </div>
        </div>
      </Surface>

      <Surface tone="raised" padding="md" className="mt-4">
        <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">Security</p>
        {isChangingPassword ? (
          <div className="mt-3 space-y-3">
            <Input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              autoFocus
            />
            <Input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />
            {newPassword.trim().length > 0 && !isLongEnough && (
              <p className="text-xs text-danger">Password must be at least {MIN_PASSWORD_LENGTH} characters.</p>
            )}
            {confirmPassword.length > 0 && !passwordsMatch && (
              <p className="text-xs text-danger">Passwords don't match.</p>
            )}
            {passwordError && <p className="text-xs text-danger">{passwordError}</p>}
            <div className="flex gap-2">
              <Button onClick={submitPasswordChange} disabled={!canSubmitPassword}>
                {passwordStatus === "saving" ? "Saving…" : "Update Password"}
              </Button>
              <Button variant="ghost" onClick={cancelChangingPassword} disabled={passwordStatus === "saving"}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-3 flex items-center gap-3">
            <Button variant="secondary" onClick={startChangingPassword}>Change Password</Button>
            {passwordStatus === "success" && <span className="text-xs text-accent-soft">Password updated</span>}
          </div>
        )}
      </Surface>

      <div className="mt-6">
        <Button variant="ghost" onClick={handleSignOut}>Sign Out</Button>
      </div>
    </div>
  );
}
