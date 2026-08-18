import { FileText } from "lucide-react";
import { HighlightedPassageText } from "./highlighted-passage-text";

export interface Passage {
  chunk_id: string;
  text: string;
  page_number: number | null;
  score: number;
}

// Scores below MIN_SIMILARITY_SCORE (0.3, enforced server-side) never reach
// the client, so this only has to spread the remaining ~0.3-1.0 range into
// a 0-100 bar rather than represent the full cosine range.
function relevancePercent(score: number) {
  const normalized = (score - 0.3) / 0.7;
  return Math.round(Math.min(1, Math.max(0, normalized)) * 100);
}

export function PassageResult({
  passage,
  rank,
  question,
}: {
  passage: Passage;
  rank: number;
  question: string;
}) {
  const relevance = relevancePercent(passage.score);

  return (
    <li className="flex gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-xs font-semibold text-accent-foreground"
        aria-hidden="true"
      >
        {rank}
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <FileText className="h-3.5 w-3.5" aria-hidden="true" />
            {passage.page_number != null ? `Page ${passage.page_number}` : "Page unknown"}
          </div>

          <div className="flex items-center gap-2" title={`Relevance score ${passage.score.toFixed(2)}`}>
            <span className="text-xs font-medium text-muted-foreground">Match</span>
            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary">
              <div className="h-full rounded-full bg-primary" style={{ width: `${relevance}%` }} />
            </div>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-foreground">
          <HighlightedPassageText text={passage.text} question={question} />
        </p>
      </div>
    </li>
  );
}
