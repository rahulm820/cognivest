"use client";

import type { QueryResponse } from "@/types";
import { CitationChip } from "@/components/common";
import { FeedbackControls } from "./FeedbackControls";

export interface AnswerPanelProps {
  answer?: QueryResponse;
  question: string;
  ticker: string;
  isLoading?: boolean;
  isError?: boolean;
  /** Choreography beat: reveal citation chips (400ms after the answer text). */
  showChips?: boolean;
}

/** Three shimmer lines — skeleton for the answer while the query is in flight. */
function AnswerSkeleton() {
  return (
    <div className="space-y-2.5" aria-label="Loading answer" aria-busy>
      <div className="shimmer h-3.5 w-[92%] rounded" />
      <div className="shimmer h-3.5 w-[78%] rounded" />
      <div className="shimmer h-3.5 w-[60%] rounded" />
    </div>
  );
}

/**
 * Renders a query answer: text fades in, then (on the `showChips` beat) citation
 * chips stagger in beneath it, then feedback controls. The chart-marker beat is
 * driven by the parent workspace, not here.
 */
export function AnswerPanel({
  answer,
  question,
  ticker,
  isLoading,
  isError,
  showChips = false,
}: AnswerPanelProps) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4 shadow-elevated">
      {isLoading ? (
        <AnswerSkeleton />
      ) : isError ? (
        <p className="text-sm text-danger">
          Query failed — the memory service may still be warming up. Try again.
        </p>
      ) : answer ? (
        <>
          <p className="animate-fade-in-up text-[15px] leading-relaxed text-foreground">
            {answer.answer}
          </p>

          {answer.citations.length > 0 ? (
            <div
              className="mt-4 flex flex-wrap gap-2 transition-opacity duration-200"
              style={{ opacity: showChips ? 1 : 0 }}
            >
              {answer.citations.map((citation, i) => (
                <CitationChip
                  key={citation.id}
                  citation={citation}
                  index={i}
                  revealed={showChips}
                />
              ))}
            </div>
          ) : null}

          <FeedbackControls ticker={ticker} question={question} />
        </>
      ) : null}
    </div>
  );
}
