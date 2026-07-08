/** Continuity-implying relative labels ("Just now," "Earlier today," "3
 * days ago") rather than exact timestamps — the notebook should read as
 * an accumulating journal, not a session-scoped transcript. */
export function relativeTime(timestamp: number, now: number = Date.now()): string {
  const diffMs = now - timestamp;
  const diffMin = diffMs / 60_000;

  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${Math.floor(diffMin)} min ago`;

  const diffHours = diffMin / 60;
  const sameDay = new Date(timestamp).toDateString() === new Date(now).toDateString();
  if (sameDay) return diffHours < 2 ? "Earlier this hour" : "Earlier today";

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;

  const diffWeeks = Math.floor(diffDays / 7);
  if (diffWeeks < 5) return `${diffWeeks} week${diffWeeks > 1 ? "s" : ""} ago`;

  const diffMonths = Math.floor(diffDays / 30);
  return `${diffMonths} month${diffMonths > 1 ? "s" : ""} ago`;
}
