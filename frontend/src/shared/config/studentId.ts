/**
 * V12 — the student's id is now the real, authenticated Supabase user's
 * id (auth.uid()), never a randomly-generated stand-in. AuthContext sets
 * it once a session resolves, before any provider that reads it can
 * mount (ProtectedRoute gates the whole app on a valid session first).
 */
let currentStudentId: string | null = null;

export function setCurrentStudentId(id: string | null): void {
  currentStudentId = id;
}

export function getCurrentStudentId(): string {
  if (!currentStudentId) {
    throw new Error("getCurrentStudentId() called before an authenticated session was established.");
  }
  return currentStudentId;
}
