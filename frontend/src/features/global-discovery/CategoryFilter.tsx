import { cn } from "../../design-system/cn";

const CATEGORIES = [
  "traditional",
  "emerging",
  "interdisciplinary",
  "research",
  "startup",
  "government",
  "non_profit",
  "country_specific",
];

export function CategoryFilter({
  selected,
  onSelect,
}: {
  selected: string | null;
  onSelect: (category: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          "rounded-full border px-3 py-1.5 text-xs transition",
          selected === null
            ? "border-accent/40 bg-accent/10 text-accent-soft"
            : "border-border text-ink-faint hover:text-ink-muted",
        )}
      >
        All
      </button>
      {CATEGORIES.map((category) => (
        <button
          key={category}
          onClick={() => onSelect(category)}
          className={cn(
            "rounded-full border px-3 py-1.5 text-xs capitalize transition",
            selected === category
              ? "border-accent/40 bg-accent/10 text-accent-soft"
              : "border-border text-ink-faint hover:text-ink-muted",
          )}
        >
          {category.replace("_", " ")}
        </button>
      ))}
    </div>
  );
}
