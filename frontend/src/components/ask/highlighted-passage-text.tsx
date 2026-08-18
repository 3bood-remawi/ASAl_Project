import { Fragment } from "react";
import { extractHighlightTerms } from "@/lib/highlight-terms";

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Renders passage text with every word that also appears in the question
 * wrapped in <mark>, so it's easy to see why the passage matched.
 */
export function HighlightedPassageText({ text, question }: { text: string; question: string }) {
  const terms = extractHighlightTerms(question);
  if (terms.length === 0) {
    return <>{text}</>;
  }

  // Longest terms first so e.g. "termination" isn't cut short by a
  // coincidental match on a shorter term earlier in the list.
  const sortedTerms = [...terms].sort((a, b) => b.length - a.length);
  const pattern = sortedTerms.map(escapeRegExp).join("|");
  const parts = text.split(new RegExp(`(\\b(?:${pattern})\\b)`, "gi"));
  const termSet = new Set(terms);

  return (
    <>
      {parts.map((part, i) =>
        termSet.has(part.toLowerCase()) ? (
          <mark key={i} className="rounded-sm bg-warning-200 px-0.5 text-inherit">
            {part}
          </mark>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        )
      )}
    </>
  );
}
