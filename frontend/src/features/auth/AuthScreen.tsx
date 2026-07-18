import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { Input } from "../../design-system/components/Input";
import { Logo } from "../../design-system/components/Logo";
import { Surface } from "../../design-system/components/Surface";
import { Layout } from "../../shared/components/Layout";
import { useAuthContext } from "../../shared/auth/AuthContext";

type Mode = "sign-in" | "sign-up";

export function AuthScreen() {
  const { signIn, signUp } = useAuthContext();
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [confirmationNotice, setConfirmationNotice] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  const isSignUp = mode === "sign-up";

  const submit = async () => {
    setIsBusy(true);
    setError(null);
    setConfirmationNotice(null);

    if (isSignUp) {
      const result = await signUp(email, password, name);
      setIsBusy(false);
      if (result.error) {
        setError(result.error);
        return;
      }
      if (result.needsConfirmation) {
        setConfirmationNotice(`Account created — check ${email} for a confirmation link, then sign in.`);
        setMode("sign-in");
        return;
      }
      navigate("/onboarding");
      return;
    }

    const result = await signIn(email, password);
    setIsBusy(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    navigate("/dashboard");
  };

  return (
    <Layout>
      <div className="flex h-full items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <div className="flex flex-col items-center">
            <Logo size="lg" withTagline />
          </div>
          <p className="mt-4 text-center text-sm text-ink-muted">
            Your career intelligence, remembered between sessions.
          </p>

          <div className="mt-8 flex gap-2">
            {(["sign-in", "sign-up"] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => {
                  setMode(m);
                  setError(null);
                  setConfirmationNotice(null);
                }}
                className={cn(
                  "flex-1 rounded-full border px-3 py-1.5 text-xs capitalize transition-colors",
                  mode === m
                    ? "border-accent-soft/40 bg-accent/10 text-accent-soft"
                    : "border-border text-ink-faint hover:border-border-strong hover:text-ink-muted",
                )}
              >
                {m === "sign-in" ? "Sign In" : "Sign Up"}
              </button>
            ))}
          </div>

          <Surface tone="raised" padding="md" className="mt-4">
            <div className="space-y-3">
              {isSignUp && (
                <Input
                  placeholder="Full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoComplete="name"
                />
              )}
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={isSignUp ? "new-password" : "current-password"}
              />
            </div>

            {confirmationNotice && <p className="mt-3 text-xs text-accent-soft">{confirmationNotice}</p>}
            {error && <p className="mt-3 text-xs text-danger">{error}</p>}

            <div className="mt-4">
              <Button
                className="w-full"
                disabled={isBusy || !email.trim() || !password.trim()}
                onClick={submit}
              >
                {isBusy ? "Please wait…" : isSignUp ? "Create Account" : "Sign In"}
              </Button>
            </div>
          </Surface>
        </div>
      </div>
    </Layout>
  );
}
