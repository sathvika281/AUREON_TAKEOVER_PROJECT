import { LayoutDashboard, Clock, LogOut, Sparkles, UserCircle } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { cn } from "../../design-system/cn";
import { Logo } from "../../design-system/components/Logo";
import { useSuggestionsContext } from "../suggestions/SuggestionsContext";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { STAGES } from "./journeyConfig";

const ACCOUNT_LINKS = [
  { to: "/dashboard", label: "Mission Control", icon: LayoutDashboard },
  { to: "/history", label: "Journey", icon: Clock },
  { to: "/profile", label: "Profile", icon: UserCircle },
];

/**
 * A slender meridian rail, not a boxed sidebar — a single hairline runs
 * the full height of the module list, each module a node along it: a
 * bright filled node when active, a hollow ring when merely available,
 * a dim hollow ring when locked. No pill backgrounds anywhere; presence
 * on the line and brightness of the label carry all the state that used
 * to live in a background fill. Same `NavLink`s, same `STAGES` /
 * `ACCOUNT_LINKS` data, same routes — only the rendering changed.
 */
export function JourneyNav() {
  const { signOut } = useAuthContext();
  const { openModal } = useSuggestionsContext();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/login");
  };

  return (
    <nav className="flex h-full w-64 shrink-0 flex-col overflow-y-auto border-r border-border bg-canvas px-6 py-7">
      <NavLink to="/" className="mb-7 block border-b border-border pb-6">
        <Logo size="sm" />
      </NavLink>

      <div className="space-y-0.5">
        {ACCOUNT_LINKS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "relative flex items-center gap-2.5 py-1.5 pl-4 text-sm transition-colors",
                isActive ? "text-ink" : "text-ink-muted hover:text-ink",
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={cn(
                    "absolute left-0 top-1/2 h-1 w-1 -translate-y-1/2 rounded-full transition-colors",
                    isActive ? "bg-accent-soft" : "bg-transparent",
                  )}
                />
                <Icon size={14} className="shrink-0" />
                <span className="truncate">{label}</span>
              </>
            )}
          </NavLink>
        ))}
        <button
          onClick={() => openModal()}
          className="relative flex w-full items-center gap-2.5 py-1.5 pl-4 text-sm text-ink-muted transition-colors hover:text-ink"
        >
          <Sparkles size={14} className="shrink-0" />
          <span>Help Aureon Grow</span>
        </button>
        <button
          onClick={handleSignOut}
          className="relative flex w-full items-center gap-2.5 py-1.5 pl-4 text-sm text-ink-muted transition-colors hover:text-ink"
        >
          <LogOut size={14} className="shrink-0" />
          <span>Logout</span>
        </button>
      </div>

      <div className="relative mt-8 space-y-7 border-l border-border pl-5">
        {STAGES.map((stage) => (
          <div key={stage.id}>
            <p className="mb-2.5 font-mono text-[0.6rem] uppercase tracking-[0.16em] text-ink-faint">
              {stage.title}
            </p>
            <div className="space-y-0.5">
              {stage.modules.map((module) => {
                const Icon = module.icon;
                return (
                  <NavLink
                    key={module.id}
                    to={module.path}
                    className={({ isActive }) =>
                      cn(
                        "relative flex items-center gap-2.5 py-1.5 text-sm transition-colors",
                        module.locked
                          ? "text-ink-faint/70"
                          : isActive
                            ? "text-ink"
                            : "text-ink-muted hover:text-ink",
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <span
                          className={cn(
                            "absolute -left-[23px] top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full border transition-colors",
                            module.locked && "border-border bg-transparent",
                            !module.locked && isActive && "border-accent-soft bg-accent-soft",
                            !module.locked && !isActive && "border-border-strong bg-canvas",
                          )}
                        />
                        <Icon size={14} className="shrink-0" />
                        <span className="truncate">{module.title}</span>
                      </>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </nav>
  );
}
