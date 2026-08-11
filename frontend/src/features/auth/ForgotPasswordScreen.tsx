import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Input } from "../../design-system/components/Input";
import { Logo } from "../../design-system/components/Logo";
import { Surface } from "../../design-system/components/Surface";
import { Layout } from "../../shared/components/Layout";
import { useAuthContext } from "../../shared/auth/AuthContext";

/**
 * Sprint 6 — the "Forgot password?" destination linked from AuthScreen's
 * sign-in mode. Deliberately its own screen rather than a third AuthScreen
 * tab — the sign-in/sign-up toggle is a closed pair, and recovery is a
 * different shape (one field, one honest outcome, no mode to switch back
 * into from here besides "Back to Sign In").
 *
 * Never confirms or denies whether the entered email belongs to a real
 * account: Supabase's own resetPasswordForEmail already returns identical
 * success for both cases, so the same generic message is shown regardless
 * — only a genuinely different failure (malformed email, rate limiting,
 * network) surfaces as a distinct error.
 */
export function ForgotPasswordScreen() {
  const { requestPasswordReset } = useAuthContext();
  const [email, setEmail] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const submit = async () => {
    setIsBusy(true);
    setError(null);
    const result = await requestPasswordReset(email.trim());
    setIsBusy(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    setIsSubmitted(true);
  };

  return (
    <Layout>
      <div className="flex h-full items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <div className="flex flex-col items-center">
            <Logo size="lg" withTagline />
          </div>
          <p className="mt-4 text-center text-sm text-ink-muted">Reset your password.</p>

          <Surface tone="raised" padding="md" className="mt-8">
            {isSubmitted ? (
              <div className="text-center">
                <p className="text-sm text-ink">Check your email</p>
                <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                  If an account exists for {email.trim()}, we've sent a link to reset your
                  password. It may take a few minutes to arrive.
                </p>
              </div>
            ) : (
              <>
                <p className="text-sm text-ink-muted">
                  Enter the email on your account and we'll send you a link to reset your
                  password.
                </p>
                <div className="mt-4">
                  <Input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                  />
                </div>

                {error && <p className="mt-3 text-xs text-danger">{error}</p>}

                <div className="mt-4">
                  <Button className="w-full" disabled={isBusy || !email.trim()} onClick={submit}>
                    {isBusy ? "Please wait…" : "Send Reset Link"}
                  </Button>
                </div>
              </>
            )}

            <Link
              to="/login"
              className="mt-4 block text-center text-xs text-ink-faint transition-colors hover:text-ink-muted"
            >
              Back to Sign In
            </Link>
          </Surface>
        </div>
      </div>
    </Layout>
  );
}
