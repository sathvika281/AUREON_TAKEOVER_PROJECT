import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

import { SplashScreen } from "../../shared/components/SplashScreen";
import { useAuthContext } from "../../shared/auth/AuthContext";

/** Gates the whole app on a valid session — redirects to /login if
 * unauthenticated, shows a branded splash while the initial session check
 * is still in flight (supabase-js resolving/restoring from localStorage). */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuthContext();

  if (isLoading) return <SplashScreen />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
