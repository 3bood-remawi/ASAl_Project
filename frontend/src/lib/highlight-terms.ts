// Common words that are almost never useful to highlight -- they show up in
// nearly every question but don't explain why a passage matched.
const STOP_WORDS = new Set([
  "a", "an", "and", "any", "are", "as", "at", "be", "been", "being", "by",
  "can", "could", "did", "do", "does", "doing", "for", "from", "had", "has",
  "have", "having", "how", "i", "if", "in", "into", "is", "it", "its", "may",
  "might", "must", "of", "on", "or", "our", "shall", "should", "so", "than",
  "that", "the", "their", "them", "then", "there", "these", "this", "those",
  "to", "up", "was", "we", "were", "what", "when", "where", "which", "who",
  "why", "will", "with", "would", "you", "your",
]);

/**
 * Pulls the distinct, meaningful words out of a question so they can be
 * highlighted wherever they appear in a passage. Short words and common
 * stop words are dropped since highlighting them adds noise rather than
 * explaining the match.
 */
export function extractHighlightTerms(question: string): string[] {
  const words = question.toLowerCase().match(/[a-z0-9']+/g) ?? [];

  const seen = new Set<string>();
  const terms: string[] = [];
  for (const word of words) {
    if (word.length < 3 || STOP_WORDS.has(word) || seen.has(word)) continue;
    seen.add(word);
    terms.push(word);
  }
  return terms;
}
