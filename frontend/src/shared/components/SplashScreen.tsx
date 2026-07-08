import { AureonMark } from "../../design-system/components/Logo";

/** Shown only while the initial session check is in flight (supabase-js
 * resolving/restoring from localStorage) — replaces what used to be a
 * blank frame with a quiet, branded pause rather than a spinner. */
export function SplashScreen() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center gap-4 bg-canvas">
      <AureonMark size={56} className="animate-pulse" />
      <p className="text-sm font-semibold tracking-wide text-ink">Aureon</p>
    </div>
  );
}
