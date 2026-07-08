/**
 * Splits on sentence boundaries while keeping punctuation. Used to pace
 * the reveal of Aureon's replies at the sentence level rather than
 * character-by-character — the backend returns a complete reply in one
 * response (no real token streaming), so pacing the *display* of
 * already-received text is an honest pacing technique, not a claim of
 * live generation. Sentence-level (rather than word-level) chunking also
 * avoids ever rendering a truncated markdown pair (e.g. an opened `**`
 * with no closing `**`) mid-reveal.
 */
export function splitIntoSentences(text: string): string[] {
  const matches = text.match(/[^.!?]+[.!?]*(\s+|$)/g);
  return matches ? matches.map((s) => s.trim()).filter(Boolean) : [text];
}
