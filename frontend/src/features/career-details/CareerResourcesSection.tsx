import { Surface } from "../../design-system/components/Surface";
import { Badge } from "../../design-system/components/Badge";

function TagList({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{label}</p>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {items.map((item) => (
          <Badge key={item} tone="cool">
            {item}
          </Badge>
        ))}
      </div>
    </div>
  );
}

function PlainList({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-[0.65rem] uppercase tracking-widest text-ink-faint">{label}</p>
      <ul className="mt-1.5 space-y-1">
        {items.map((item) => (
          <li key={item} className="text-sm leading-relaxed text-ink-muted">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Explore Polish Batch — "how would I actually get there / go deeper,"
 * grouped into where this career lives (industries/companies/research)
 * and how to build real momentum toward it (education, funding, and
 * hands-on learning resources).
 */
export function CareerResourcesSection({
  relatedIndustries,
  researchAreas,
  companies,
  universities,
  scholarships,
  competitions,
  certifications,
  books,
  videos,
  communities,
  openSourceProjects,
  projects,
}: {
  relatedIndustries: string[];
  researchAreas: string[];
  companies: string[];
  universities: string[];
  scholarships: string[];
  competitions: string[];
  certifications: string[];
  books: string[];
  videos: string[];
  communities: string[];
  openSourceProjects: string[];
  projects: string[];
}) {
  const hasAny =
    relatedIndustries.length > 0 ||
    researchAreas.length > 0 ||
    companies.length > 0 ||
    universities.length > 0 ||
    scholarships.length > 0 ||
    competitions.length > 0 ||
    certifications.length > 0 ||
    books.length > 0 ||
    videos.length > 0 ||
    communities.length > 0 ||
    openSourceProjects.length > 0 ||
    projects.length > 0;
  if (!hasAny) return null;

  return (
    <Surface tone="raised" padding="lg" className="space-y-4">
      <TagList label="Related industries" items={relatedIndustries} />
      <TagList label="Real research areas in this field" items={researchAreas} />
      <TagList label="Companies working in this space" items={companies} />
      <PlainList label="Universities known for this field" items={universities} />
      <PlainList label="Scholarships to look into" items={scholarships} />
      <PlainList label="Competitions worth entering" items={competitions} />
      <PlainList label="Certifications worth pursuing" items={certifications} />
      <PlainList label="Books worth reading" items={books} />
      <PlainList label="Videos worth watching" items={videos} />
      <PlainList label="Communities to join" items={communities} />
      <PlainList label="Open-source projects to explore" items={openSourceProjects} />
      <PlainList label="Projects to try building" items={projects} />
    </Surface>
  );
}
