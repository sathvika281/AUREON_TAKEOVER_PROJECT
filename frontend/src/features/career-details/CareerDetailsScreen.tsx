import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ShieldAlert, Sparkles } from "lucide-react";

import { Button } from "../../design-system/components/Button";
import { EmptyStatePanel } from "../../design-system/components/EmptyStatePanel";
import { PageHeader } from "../../design-system/components/PageHeader";
import { ApiError, apiClient } from "../../shared/api/client";
import type { CareerDetail } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";
import { CandidateCard } from "../career-intelligence/CandidateCard";
import { useCareerIntelligenceContext } from "../career-intelligence/CareerIntelligenceContext";
import { useCareerExplorationContext } from "../career-exploration/CareerExplorationContext";
import { useSuggestionsContext } from "../suggestions/SuggestionsContext";
import { TimelineComparison } from "../future-lens/TimelineComparison";
import { CareerCompaniesSection } from "./CareerCompaniesSection";
import { CareerDeepDiveSection } from "./CareerDeepDiveSection";
import { CareerFAQSection } from "./CareerFAQSection";
import { CareerProjectsSection } from "./CareerProjectsSection";
import { CareerResourcesSection } from "./CareerResourcesSection";
import { CareerSkillsSection } from "./CareerSkillsSection";
import { HumanStoriesSection } from "./HumanStoriesSection";
import { RealitySection } from "./RealitySection";
import { RelatedExplorationSection } from "./RelatedExplorationSection";
import { WhyPeopleLoveItSection } from "./WhyPeopleLoveItSection";

export function CareerDetailsScreen() {
  const { careerId } = useParams<{ careerId: string }>();
  const studentId = useRef(getCurrentStudentId()).current;
  const [career, setCareer] = useState<CareerDetail | null>(null);
  // A career genuinely not existing and a request that failed to reach
  // Aureon's servers are different states — this is the core detail page
  // students land on most, so conflating them is especially costly.
  const [status, setStatus] = useState<"loading" | "success" | "not-found" | "error">("loading");
  const { recordEvent, isBookmarked } = useCareerExplorationContext();
  const {
    candidates, isAnalyzing, analyzeCareers, shortlistCandidate, removeCandidate, ensureLoaded: ensureCandidatesLoaded,
  } = useCareerIntelligenceContext();

  useEffect(() => {
    ensureCandidatesLoaded();
  }, [ensureCandidatesLoaded]);
  const { openModal } = useSuggestionsContext();

  const loadCareer = useCallback(() => {
    if (!careerId) return;
    setStatus("loading");
    apiClient
      .get<CareerDetail>(`/v1/careers/${careerId}?student_id=${studentId}`)
      .then((r) => {
        setCareer(r);
        setStatus("success");
      })
      .catch((err) => setStatus(err instanceof ApiError && err.status === 404 ? "not-found" : "error"));
  }, [careerId, studentId]);

  useEffect(() => {
    loadCareer();
  }, [loadCareer]);

  useEffect(() => {
    if (!career) return;
    void recordEvent(career.id, "opened", { career_name: career.name });
    void recordEvent(career.id, "reality_read", { career_name: career.name });
    if (career.stories.length > 0) {
      void recordEvent(career.id, "story_viewed", { career_name: career.name });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [career?.id]);

  if (status === "loading") {
    return <div className="mx-auto max-w-2xl px-6 py-10 text-sm text-ink-faint">Loading…</div>;
  }

  if (status === "not-found") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="text-sm text-ink-faint">Career not found.</p>
        <Link to="/explore/career-reality" className="mt-2 inline-block text-sm text-accent-soft">
          Back to Career Explorer
        </Link>
      </div>
    );
  }

  if (status === "error" || !career) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <EmptyStatePanel
          icon={ShieldAlert}
          title="Couldn't Load This Career"
          description="Something went wrong reaching Aureon's servers — this isn't the same as the career not existing. Try again."
          action={<Button variant="secondary" onClick={loadCareer}>Retry</Button>}
        />
      </div>
    );
  }

  const bookmarked = isBookmarked(career.id);
  const matchedCandidate = candidates.find((c) => c.career_id === career.id) ?? null;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/explore/career-reality" className="text-xs text-ink-faint hover:text-ink-muted">
        ← Career Explorer
      </Link>
      <PageHeader
        className="mt-2"
        title={career.name}
        description={career.one_liner}
        action={
          <div className="flex flex-col items-end gap-2">
            <Button
              variant="ghost"
              size="md"
              onClick={() =>
                recordEvent(career.id, bookmarked ? "removed" : "bookmarked", { career_name: career.name })
              }
            >
              {bookmarked ? "Bookmarked" : "Bookmark"}
            </Button>
            <button
              onClick={() =>
                openModal({
                  category: "correction",
                  context_type: "career",
                  context_id: career.id,
                  context_metadata: { page_or_feature: "Career Explorer", career_name: career.name },
                })
              }
              className="text-xs text-ink-faint transition-colors hover:text-ink-muted"
            >
              Suggest a correction
            </button>
          </div>
        }
      />

      <div className="mt-6">
        <Link to="/decide/decision-lab" className="text-xs text-accent-soft hover:text-accent">
          Simulate this path in Decision Lab →
        </Link>
      </div>

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        What careers fit me
      </p>
      {matchedCandidate ? (
        <CandidateCard candidate={matchedCandidate} onShortlist={shortlistCandidate} onRemove={removeCandidate} />
      ) : (
        <div className="flex items-start gap-3 border-l border-border-strong pl-4">
          <Sparkles size={16} className="mt-0.5 shrink-0 text-accent-soft" />
          <div className="flex-1">
            <p className="text-sm leading-relaxed text-ink-muted">
              Aureon hasn't reasoned about this career against your Career DNA yet.
            </p>
            <Button size="md" className="mt-3" onClick={analyzeCareers} disabled={isAnalyzing}>
              {isAnalyzing ? "Analyzing…" : "Analyze how well this fits you"}
            </Button>
          </div>
        </div>
      )}

      <WhyPeopleLoveItSection
        description={career.description}
        whyPeopleLoveIt={career.why_people_love_it}
        branches={career.branches}
      />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Career Reality
      </p>
      <RealitySection reality={career.reality} />

      {career.required_skills.length > 0 && (
        <div className="mt-4">
          <CareerSkillsSection skills={career.required_skills} />
        </div>
      )}

      {career.hiring_companies.length > 0 && (
        <div className="mt-4">
          <CareerCompaniesSection companies={career.hiring_companies} />
        </div>
      )}

      {career.related_projects.length > 0 && (
        <div className="mt-4">
          <CareerProjectsSection projects={career.related_projects} />
        </div>
      )}

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        A Day and Week in This Career
      </p>
      <CareerDeepDiveSection
        dayInTheLife={career.day_in_the_life}
        weeklyRoutine={career.weekly_routine}
        dailyTools={career.daily_tools}
        careerProgression={career.career_progression}
      />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Future Outlook
      </p>
      <TimelineComparison careerName={career.name} futureLens={career.future_lens} />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Human Stories
      </p>
      <HumanStoriesSection stories={career.stories} />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Build Your Path
      </p>
      <CareerResourcesSection
        relatedIndustries={career.related_industries}
        researchAreas={career.research_areas}
        companies={career.companies}
        universities={career.universities}
        scholarships={career.scholarships}
        competitions={career.competitions}
        certifications={career.certifications}
        books={career.books}
        videos={career.videos}
        communities={career.communities}
        openSourceProjects={career.open_source_projects}
        projects={career.projects}
      />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Good to Know
      </p>
      <CareerFAQSection commonMisconceptions={career.common_misconceptions} faqs={career.faqs} />

      <p className="mb-2 mt-8 px-1 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        Explore Further
      </p>
      <RelatedExplorationSection
        relatedCareers={career.related_careers}
        adjacentCareers={career.adjacent_careers}
        recommendedNextExploration={career.recommended_next_exploration}
        relatedTrends={career.related_trends}
      />
    </div>
  );
}
