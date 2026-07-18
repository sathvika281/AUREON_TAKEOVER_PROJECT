import type { Session, User } from "@supabase/supabase-js";
import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { setAuthToken } from "../api/client";
import { setCurrentStudentId } from "../config/studentId";
import { supabase } from "./supabaseClient";

interface AuthContextValue {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  signUp: (email: string, password: string, name: string) => Promise<{ error: string | null; needsConfirmation: boolean }>;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  completeOnboarding: (data: Record<string, unknown>) => Promise<{ error: string | null }>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/** Session persistence and automatic restore come for free from
 * supabase-js (it stores the session in localStorage and refreshes it) —
 * this just mirrors that state into the rest of the app: the auth token
 * on every API call (shared/api/client.ts) and the student id every
 * provider reads (shared/config/studentId.ts). */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      applySession(data.session);
      setIsLoading(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      applySession(newSession);
    });

    return () => subscription.subscription.unsubscribe();
  }, []);

  function applySession(newSession: Session | null) {
    setSession(newSession);
    setAuthToken(newSession?.access_token ?? null);
    setCurrentStudentId(newSession?.user.id ?? null);
  }

  async function signUp(email: string, password: string, name: string) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: name ? { name } : undefined },
    });
    // Supabase returns a real user + a null session (no error) when the
    // project requires email confirmation — sign-up succeeded, but there's
    // no session to log the student in with yet. Told apart from a genuine
    // failure so the screen can say so honestly instead of silently
    // bouncing back to /login.
    const needsConfirmation = !error && !!data.user && !data.session;
    return { error: error?.message ?? null, needsConfirmation };
  }

  async function signIn(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  }

  async function signOut() {
    await supabase.auth.signOut();
  }

  /** Real, persisted Supabase user_metadata — the same mechanism signUp's
   * `name` field already uses. Serves both the initial onboarding wizard
   * (a full payload) and every later Curiosity Check-in answer (a
   * partial payload merged into the same fields) — never a separate
   * store, and nothing written here is ever treated as a permanent,
   * unchangeable label. */
  async function completeOnboarding(data: Record<string, unknown>) {
    const { error } = await supabase.auth.updateUser({ data });
    return { error: error?.message ?? null };
  }

  const value: AuthContextValue = {
    user: session?.user ?? null,
    session,
    isLoading,
    signUp,
    signIn,
    signOut,
    completeOnboarding,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return ctx;
}
