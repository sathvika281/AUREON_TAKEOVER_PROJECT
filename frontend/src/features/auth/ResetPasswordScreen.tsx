import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Logo } from "../../design-system/components/Logo";
import { Surface } from "../../design-system/components/Surface";
import { Layout } from "../../shared/components/Layout";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { supabase } from "../../shared/auth/supabaseClient";

const MIN_PASSWORD_LENGTH = 6;

/** How long to wait for Supabase's own recovery-link URL processing
 * before honestly concluding the link is invalid/expired — processing
 * is local token parsing, not a slow round trip, so this only needs to
 * cover a real render/tick delay, not network latency. */
const RECOVERY_DETECTION_TIMEOUT_MS = 4000;

/**
 * Sprint 6 — where a password-reset email link lands. Deliberately does
 * NOT gate on AuthContext's general `user`/session state: a student who
 * is already logged into a *different* account in this browser, then
 * opens a stale or already-used recovery link, must still see an honest
 * "invalid or expired" message rather than silently falling back to
 * their unrelated existing session. Supabase fires a distinct
 * `PASSWORD_RECOVERY` auth event only when it has just verified a real
 * recovery token from the URL — that event, not general session
 * presence, is the only signal trusted here.
 */
export function ResetPasswordScreen() {
  const { updatePassword, signOut } = useAuthContext();

  const [recoveryConfirmed, setRecoveryConfirmed] = useState(false);
  const [hasWaitedForRecovery, setHasWaitedForRecovery] = useState(false);

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    const { data: subscription } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") setRecoveryConfirmed(true);
    });
    const timeout = setTimeout(() => setHasWaitedForRecovery(true), RECOVERY_DETECTION_TIMEOUT_MS);
    return () => {
      subscription.subscription.unsubscribe();
      clearTimeout(timeout);
    };
  }, []);

  const passwordsMatch = password === confirmPassword;
  const isLongEnough = password.trim().length >= MIN_PASSWORD_LENGTH;
  const canSubmit = isLongEnough && passwordsMatch && !isSaving;

  const submit = async () => {
    if (!canSubmit) return;
    setIsSaving(true);
    setError(null);
    const result = await updatePassword(password);
    setIsSaving(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    // A recovery link's session is a means to prove identity for this
    // one action, not a substitute for a real login — matches the
    // requested flow (successful update -> return to login), and
    // avoids leaving a recovery-derived session active afterward.
    await signOut();
    setIsDone(true);
  };

  return (
    <Layout>
      <div className="flex h-full items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <div className="flex flex-col items-center">
            <Logo size="lg" withTagline />
          </div>
          <p className="mt-4 text-center text-sm text-ink-muted">Choose a new password.</p>

          <Surface tone="raised" padding="md" className="mt-8">
            {isDone ? (
              <div className="text-center">
                <p className="text-sm text-ink">Password updated</p>
                <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                  Your password has been changed. Sign in below using your new password.
                </p>
                <Link to="/login">
                  <Button className="mt-4 w-full">Back to Sign In</Button>
                </Link>
              </div>
            ) : !recoveryConfirmed ? (
              hasWaitedForRecovery ? (
                <div className="text-center">
                  <p className="text-sm text-ink">This link is invalid or has expired</p>
                  <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                    Password reset links only work once and expire after a while. Request a new
                    one to continue.
                  </p>
                  <Link to="/forgot-password">
                    <Button className="mt-4 w-full">Request a New Link</Button>
                  </Link>
                  <Link
                    to="/login"
                    className="mt-3 block text-center text-xs text-ink-faint transition-colors hover:text-ink-muted"
                  >
                    Back to Sign In
                  </Link>
                </div>
              ) : (
                <p className="text-center text-sm text-ink-faint">Verifying your link…</p>
              )
            ) : (
              <>
                <p className="text-sm text-ink-muted">
                  Enter a new password for your account.
                </p>
                <div className="mt-4 space-y-3">
                  <Input
                    type="password"
                    placeholder="New password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                  <Input
                    type="password"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                </div>

                {password.trim().length > 0 && !isLongEnough && (
                  <p className="mt-3 text-xs text-danger">
                    Password must be at least {MIN_PASSWORD_LENGTH} characters.
                  </p>
                )}
                {confirmPassword.length > 0 && !passwordsMatch && (
                  <p className="mt-3 text-xs text-danger">Passwords don't match.</p>
                )}
                {error && <p className="mt-3 text-xs text-danger">{error}</p>}

                <div className="mt-4">
                  <Button className="w-full" disabled={!canSubmit} onClick={submit}>
                    {isSaving ? "Saving…" : "Update Password"}
                  </Button>
                </div>
              </>
            )}
          </Surface>
        </div>
      </div>
    </Layout>
  );
}
