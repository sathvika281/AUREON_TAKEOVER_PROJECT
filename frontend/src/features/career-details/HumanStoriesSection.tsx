import { Badge } from "../../design-system/components/Badge";
import { Surface } from "../../design-system/components/Surface";
import type { CareerStory } from "../../shared/api/types";

/**
 * Illustrative composite personas (labeled by role/experience), not
 * fabricated named real individuals — consistent with this product's
 * anti-fabrication standard. Architecture supports many stories per
 * career; relevance tagging (simple trait-tag overlap, not embeddings)
 * surfaces the ones most connected to the student's own Career DNA.
 */
export function HumanStoriesSection({ stories }: { stories: CareerStory[] }) {
  if (stories.length === 0) {
    return (
      <p className="text-sm text-ink-faint">
        No human stories for this career yet — the architecture supports adding them over time.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {stories.map((story) => (
        <Surface key={story.id} tone="neutral" padding="md">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium text-ink">{story.person_label}</p>
            {story.relevant_to_student && <Badge tone="cool">Relevant to you</Badge>}
          </div>
          <div className="mt-3 space-y-2 text-sm leading-relaxed text-ink-muted">
            <p>
              <span className="text-ink-faint">Background: </span>
              {story.background}
            </p>
            <p>
              <span className="text-ink-faint">Journey: </span>
              {story.journey}
            </p>
            <p>
              <span className="text-ink-faint">Challenges: </span>
              {story.challenges}
            </p>
            <p>
              <span className="text-ink-faint">Turning point: </span>
              {story.turning_points}
            </p>
            <p className="italic">
              <span className="not-italic text-ink-faint">Advice: </span>
              {story.advice}
            </p>
          </div>
        </Surface>
      ))}
    </div>
  );
}
