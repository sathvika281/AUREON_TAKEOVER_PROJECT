import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../../design-system/components/Button";
import { apiClient } from "../../shared/api/client";
import type { CareerDetail } from "../../shared/api/types";
import { getCurrentStudentId } from "../../shared/config/studentId";
import { useCareerExplorationContext } from "../career-exploration/CareerExplorationContext";
import { HumanStoriesSection } from "./HumanStoriesSection";
import { RealitySection } from "./RealitySection";

export function CareerDetailsScreen() {
  const { careerId } = useParams<{ careerId: string }>();
  const studentId = useRef(getCurrentStudentId()).current;
  const [career, setCareer] = useState<CareerDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { recordEvent, isBookmarked } = useCareerExplorationContext();

  useEffect(() => {
    if (!careerId) return;
    setIsLoading(true);
    apiClient
      .get<CareerDetail>(`/v1/careers/${careerId}?student_id=${studentId}`)
      .then(setCareer)
      .catch(() => setCareer(null))
      .finally(() => setIsLoading(false));
  }, [careerId, studentId]);

  useEffect(() => {
    if (!career) return;
    void recordEvent(career.id, "opened", { career_name: career.name });
    void recordEvent(career.id, "reality_read", { career_name: career.name });
    if (career.stories.length > 0) {
      void recordEvent(career.id, "story_viewed", { career_name: career.name });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [career?.id]);

  if (isLoading) {
    return <div className="mx-auto max-w-2xl px-6 py-10 text-sm text-ink-faint">Loading…</div>;
  }

  if (!career) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="text-sm text-ink-faint">Career not found.</p>
        <Link to="/explore/career-reality" className="mt-2 inline-block text-sm text-accent-soft">
          Back to Career Reality
        </Link>
      </div>
    );
  }

  const bookmarked = isBookmarked(career.id);

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/explore/career-reality" className="text-xs text-ink-faint hover:text-ink-muted">
        ← Career Reality
      </Link>
      <div className="mt-2 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-light text-ink">{career.name}</h1>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">{career.one_liner}</p>
        </div>
        <Button
          variant="ghost"
          size="md"
          onClick={() =>
            recordEvent(career.id, bookmarked ? "removed" : "bookmarked", { career_name: career.name })
          }
          className="shrink-0"
        >
          {bookmarked ? "Bookmarked" : "Bookmark"}
        </Button>
      </div>

      <div className="mt-6">
        <Link
          to={`/explore/future-lens?career=${career.id}`}
          className="text-xs text-accent-soft hover:text-accent"
        >
          See this career's Future Lens →
        </Link>
      </div>

      <p className="mb-2 mt-8 px-1 text-xs uppercase tracking-widest text-ink-faint">
        Career Reality
      </p>
      <RealitySection reality={career.reality} />

      <p className="mb-2 mt-8 px-1 text-xs uppercase tracking-widest text-ink-faint">
        Human Stories
      </p>
      <HumanStoriesSection stories={career.stories} />
    </div>
  );
}
