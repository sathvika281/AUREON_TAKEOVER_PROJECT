# Aureon — Security

This document describes Aureon's actual, implemented security practices —
grounded in the codebase and in live verification performed during this
project's account-lifecycle sprints (Sprints 6-11). It makes no claims
beyond what's implemented and tested. **Aureon has not undergone a formal
third-party security audit or certification** — nothing below should be
read as claiming one.

## Authentication

- **Supabase Auth** (email + password) is the sole authentication
  mechanism — no magic links, no OTP/passwordless flow, no social login.
  The frontend's Supabase client (`shared/auth/supabaseClient.ts`) is used
  *only* for auth (sign up/in/out, session persistence); all product data
  access flows through the FastAPI backend, never a direct client-side
  Supabase table query.
- **Aureon's own database never stores a password.** Supabase Auth owns
  credential storage and verification entirely; the backend never sees or
  persists a raw or hashed password anywhere in `student_profiles` or any
  other table.
- Every backend request is authenticated by re-verifying the bearer token
  against Supabase's own Auth server (`auth.get_user(token)` — a real
  network call, not local JWT decoding) via `get_current_user_id()`
  (`api/deps.py`). An invalid or expired token is rejected with `401`
  before any route logic runs.

## Authorization — student-scoped access

Every `/students/{student_id}/...` router (all student-scoped endpoints —
onboarding, discovery, projects, decision, history, and more) is gated by
`require_own_profile`, applied once at the router level so it protects
every route in that file without per-route boilerplate:

```python
async def require_own_profile(student_id: str, user_id: Annotated[str, Depends(get_current_user_id)]) -> str:
    if user_id != student_id:
        raise HTTPException(status_code=403, detail="You can only access your own profile.")
    return student_id
```

This means the path's `student_id` must exactly match the verified,
authenticated user's own id — a student can never read or write another
student's profile, evidence, or history by manipulating a URL. **Live
cross-account isolation was verified directly**, not just reasoned about:
one authenticated account's token used against a second account's
`student_id` returns `403` in practice, confirmed via real HTTP calls
against the running backend during Sprint 11's audit.

`RLS` (Row Level Security) is intentionally off in Supabase — the backend
authenticates to Supabase with a service-role key and enforces the
per-student boundary itself, in application code, via the dependency
above. This is a deliberate architectural choice (application-level
authorization, not database-level), not an oversight.

## Protected routes and session behavior

- `ProtectedRoute` gates the entire authenticated app on a valid Supabase
  session; an unauthenticated visitor is redirected to `/login`.
- `OnboardingGate` sits inside it, redirecting an authenticated-but-not-
  yet-onboarded student to `/onboarding` — a pre-existing account created
  before this gate existed is honestly treated as "onboarding incomplete"
  too, never backfilled with fabricated answers.
- **Logout** (`signOut()`) clears the Supabase session; the frontend's
  in-memory auth token and current-student-id are cleared in the same
  state-change handler, and the whole authenticated route subtree
  (including every feature provider) unmounts on the resulting redirect
  to `/login` — live-verified to leave no stale state visible to whoever
  signs in next in the same browser tab.

## Password recovery

- The "forgot password" flow always shows the same generic confirmation
  ("If an account exists for this email, we've sent a link...") regardless
  of whether the account actually exists — **no user enumeration** through
  this flow, verified directly.
- The reset-password screen distrusts general session presence and relies
  specifically on Supabase's `PASSWORD_RECOVERY` auth event (plus, since
  Sprint 11, a check of the current session's own auth method for the
  hard-refresh case) — a student who opens a stale or already-used
  recovery link sees an honest "invalid or expired" message, live-verified
  against real, expired/reused Supabase tokens, never a silent fallback to
  an unrelated existing session.
- After a successful password reset, the recovery-derived session is
  explicitly signed out before the student is sent back to a normal login
  — a recovery session is treated as proof of identity for one action, not
  a substitute for a real login.

## Password change (from an authenticated session)

Profile's "Change Password" reuses Supabase's own `updateUser({password})`
call from the student's normal, already-authenticated session — the same
underlying mechanism the recovery flow uses, not a second implementation.
Confirmed live: the old password is rejected immediately afterward, the
new one is accepted, and — matching Supabase's actual, real behavior — the
current session is *not* forcibly invalidated (a plain password change
doesn't revoke your own ongoing session; this is standard behavior, not a
weakened posture).

## What's explicitly not implemented

Named honestly rather than left ambiguous:

- No multi-factor authentication.
- No social login.
- No account deletion flow.
- No email-change flow.
- No formal migration/CI pipeline enforcing schema changes (tracked in
  the Technical Debt Register as the one item flagged "must change before
  real production").

## Secrets

`.env` (backend and frontend) is git-ignored; only `.env.example` files
(placeholder values only) are committed. No `SUPABASE_SERVICE_ROLE_KEY`,
API key, or credential has ever been committed to this repository — a
direct scan of every tracked file and the full git history found zero
matches for real key-shaped values. Render deployment secrets are
injected via the Render dashboard, never checked into `render.yaml`.
