import { useState } from "react";
import { GraduationCap, ScanSearch, Sparkles, Users } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { cn } from "../../design-system/cn";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { ProcessSteps } from "../../design-system/components/ProcessSteps";
import { MissionWorkspace } from "../mission-workspace/MissionWorkspace";
import { CollegeMatchCard } from "./CollegeMatchCard";
import { useDecisionContext } from "./DecisionContext";
import { MentorMatchCard } from "./MentorMatchCard";

type Toggle = "mentors" | "institutions";

const METHODOLOGY_STEPS = [
  {
    icon: ScanSearch,
    title: "Reads your Career DNA and interests",
    description: "Matching starts from the same evidence used everywhere else in Aureon — never a separate profile or a fresh set of quiz answers.",
  },
  {
    icon: Users,
    title: "Compares thinking style, not popularity",
    description: "Mentors and institutions are evaluated against how you think and what you value — there's no ranking by rating, followers, or prestige.",
  },
  {
    icon: Sparkles,
    title: "Every match explains itself",
    description: "Each result states specifically why it was matched to you, using the same evidence-and-reasoning discipline as the rest of Decision Lab.",
  },
];

export function MentorMatchScreen() {
  const [toggle, setToggle] = useState<Toggle>("mentors");
  const {
    mentorMatches, collegeMatches, isBusy, error, analyzeMentors, analyzeColleges,
    lastMentorMission, lastMentorArtifactsUpdated, lastCollegeMission, lastCollegeArtifactsUpdated,
  } = useDecisionContext();

  const isMentors = toggle === "mentors";
  const matches = isMentors ? mentorMatches : collegeMatches;
  const onAnalyze = isMentors ? analyzeMentors : analyzeColleges;
  const mission = isMentors ? lastMentorMission : lastCollegeMission;
  const artifactsUpdated = isMentors ? lastMentorArtifactsUpdated : lastCollegeArtifactsUpdated;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="text-2xl font-light text-ink">Mentor Match</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Matched by Career DNA, interests, and thinking style — never by popularity, never ranked.
      </p>

      <div className="mt-8">
        <ProcessSteps title="Matching Methodology" steps={METHODOLOGY_STEPS} />
      </div>

      <div className="mt-6 flex gap-2">
        {(["mentors", "institutions"] as Toggle[]).map((t) => (
          <button
            key={t}
            onClick={() => setToggle(t)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs capitalize transition",
              toggle === t
                ? "border-accent/40 bg-accent/10 text-accent-soft"
                : "border-border text-ink-faint hover:text-ink-muted",
            )}
          >
            {t === "mentors" ? "Mentors" : "Institutions (College Match)"}
          </button>
        ))}
      </div>

      <div className="mt-6">
        <Button onClick={onAnalyze} disabled={isBusy}>
          {isBusy ? "Analyzing…" : `Find ${isMentors ? "Mentors" : "Institutions"}`}
        </Button>
      </div>

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {matches.length === 0 ? (
        <div className="mt-6">
          <EmptyStatePanel
            icon={isMentors ? Users : GraduationCap}
            title={`No ${isMentors ? "Mentor" : "Institution"} Matches Yet`}
            description={`Run the analysis above to see ${isMentors ? "mentors" : "institutions"} matched against your Career DNA. This requires enough evidence for Aureon to reason about fit responsibly — build up your Career DNA in Identity Discovery if the result comes back empty.`}
          />
        </div>
      ) : mission ? (
        <div className="mt-8">
          <MissionWorkspace
            snapshot={mission}
            artifactsUpdated={artifactsUpdated}
            finalReport={
              <div className="space-y-4">
                {isMentors
                  ? mentorMatches.map((m) => <MentorMatchCard key={m.mentor_id} match={m} />)
                  : collegeMatches.map((m) => <CollegeMatchCard key={m.institution_id} match={m} />)}
              </div>
            }
          />
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {isMentors
            ? mentorMatches.map((m) => <MentorMatchCard key={m.mentor_id} match={m} />)
            : collegeMatches.map((m) => <CollegeMatchCard key={m.institution_id} match={m} />)}
        </div>
      )}
    </div>
  );
}
