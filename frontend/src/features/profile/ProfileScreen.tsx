import { useNavigate } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { Surface } from "../../design-system/components/Surface";
import { useAuthContext } from "../../shared/auth/AuthContext";
import { useDiscoveryContext } from "../discovery/DiscoveryContext";
import { useHistoryContext } from "../history/HistoryContext";

const TOTAL_CAREER_DNA_TRAITS = 10;

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

export function ProfileScreen() {
  const { user, signOut } = useAuthContext();
  const { careerDna } = useDiscoveryContext();
  const { items } = useHistoryContext();
  const navigate = useNavigate();

  const name = (user?.user_metadata?.name as string | undefined) || null;
  const traitCount = Object.keys(careerDna).length;
  const latestInvestigation = items.find((i) => i.mission_type === "search_investigation");
  const latestSimulation = items.find((i) => i.mission_type === "career_simulation");

  const handleSignOut = async () => {
    await signOut();
    navigate("/login");
  };

  return (
    <div className="mx-auto max-w-xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Profile</h1>

      <Surface tone="raised" padding="md" className="mt-8">
        <div className="space-y-2 text-sm">
          {name && (
            <p><span className="text-ink-faint">Name: </span><span className="text-ink">{name}</span></p>
          )}
          <p><span className="text-ink-faint">Email: </span><span className="text-ink">{user?.email}</span></p>
          {user?.created_at && (
            <p><span className="text-ink-faint">Member since: </span><span className="text-ink">{formatDate(user.created_at)}</span></p>
          )}
        </div>
      </Surface>

      <Surface tone="neutral" padding="md" className="mt-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Career DNA Completion</p>
            <p className="mt-1 text-ink">{traitCount}/{TOTAL_CAREER_DNA_TRAITS} traits</p>
          </div>
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Total Missions</p>
            <p className="mt-1 text-ink">{items.length}</p>
          </div>
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Latest Investigation</p>
            <p className="mt-1 text-ink-muted">{latestInvestigation?.mission_name ?? "None yet"}</p>
          </div>
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Latest Simulation</p>
            <p className="mt-1 text-ink-muted">{latestSimulation?.mission_name ?? "None yet"}</p>
          </div>
          <div>
            <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">Latest Progress Report</p>
            <p className="mt-1 text-ink-muted">
              Progress is always computed live —{" "}
              <a href="/build/progress-intelligence" className="text-accent-soft hover:underline">view current report</a>.
            </p>
          </div>
        </div>
      </Surface>

      <div className="mt-6">
        <Button variant="ghost" onClick={handleSignOut}>Sign Out</Button>
      </div>
    </div>
  );
}
