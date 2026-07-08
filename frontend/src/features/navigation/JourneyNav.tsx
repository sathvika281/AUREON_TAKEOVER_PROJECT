import { LayoutDashboard, Clock, LogOut, UserCircle } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { cn } from "../../design-system/cn";
import { Logo } from "../../design-system/components/Logo";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { STAGES } from "./journeyConfig";

const ACCOUNT_LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/history", label: "History", icon: Clock },
  { to: "/profile", label: "Profile", icon: UserCircle },
];

/**
 * A persistent roadmap, not a dropdown menu — the four stages of
 * Aureon's product vision, always visible, with the current module
 * highlighted. Locked modules (no real backend behind them yet) are
 * visually quieter, not hidden — the roadmap itself is honest about
 * what's real today.
 */
export function JourneyNav() {
  const { signOut } = useAuthContext();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/login");
  };

  return (
    <nav className="flex h-full w-64 shrink-0 flex-col overflow-y-auto border-r border-border bg-surface px-4 py-6">
      <NavLink to="/" className="px-2 pb-5 mb-1 border-b border-border block">
        <Logo size="sm" />
      </NavLink>

      <div className="mt-6 space-y-0.5">
        {ACCOUNT_LINKS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm transition-colors text-ink-muted",
                isActive && "bg-accent/10 text-ink",
                !isActive && "hover:text-ink",
              )
            }
          >
            <Icon size={15} className="shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
        <button
          onClick={handleSignOut}
          className="flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-ink-muted transition-colors hover:text-ink"
        >
          <LogOut size={15} className="shrink-0" />
          <span>Logout</span>
        </button>
      </div>

      <div className="mt-6 space-y-7">
        {STAGES.map((stage) => (
          <div key={stage.id}>
            <p className="px-2 text-[0.65rem] font-medium uppercase tracking-widest text-ink-faint">
              {stage.title}
            </p>
            <div className="mt-2 space-y-0.5">
              {stage.modules.map((module) => {
                const Icon = module.icon;
                return (
                  <NavLink
                    key={module.id}
                    to={module.path}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm transition-colors",
                        module.locked ? "text-ink-faint/70" : "text-ink-muted",
                        isActive && !module.locked && "bg-accent/10 text-ink",
                        isActive && module.locked && "bg-white/[0.03] text-ink-faint",
                        !isActive && "hover:text-ink",
                      )
                    }
                  >
                    <Icon size={15} className="shrink-0" />
                    <span className="truncate">{module.title}</span>
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
