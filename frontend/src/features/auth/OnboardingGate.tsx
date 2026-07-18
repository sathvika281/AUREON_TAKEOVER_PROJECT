import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

import { useAuthContext } from "../../shared/auth/AuthContext";

/** Sits inside ProtectedRoute — redirects to /onboarding when a
 * genuinely authenticated student hasn't completed the (now trimmed)
 * onboarding wizard yet, so a refresh or closed tab mid-wizard never
 * leaves them in the app with no profile context. A pre-existing
 * account created before this gate existed is honestly treated as
 * "onboarding incomplete" too — no fabricated backfill of answers it
 * never collected. */
export function OnboardingGate({ children }: { children: ReactNode }) {
  const { user } = useAuthContext();

  if (user && user.user_metadata?.onboarding_completed !== true) {
    return <Navigate to="/onboarding" replace />;
  }
  return <>{children}</>;
}
