"use client";

import * as React from "react";
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

/** Short "just now / N min ago" label, captured when the answer arrives. */
function useAnsweredAt(answer?: QueryResponse) {
  const [at, setAt] = React.useState<Date | null>(null);
  React.useEffect(() => {
    if (answer) setAt(new Date());
    else setAt(null);
  }, [answer]);
  return at;
}

/**
 * Renders a query answer: text fades in, then (on the `showChips` beat) citation
 * chips stagger in beneath it, then feedback controls. The chart-marker beat is
 * driven by the parent workspace, not here. A thin emerald left-accent marks
 * this as a grounded, cited response.
 */
export function AnswerPanel({
  answer,
  question,
  ticker,
  isLoading,
  isError,
  showChips = false,
}: AnswerPanelProps) {
  const answeredAt = useAnsweredAt(isLoading || isError ? undefined : answer);

  return (
    <div className="rounded-xl border border-l-2 border-border border-l-primary/70 bg-surface p-4 shadow-elevated">
      {isLoading ? (
        <AnswerSkeleton />
      ) : isError ? (
        <p className="text-sm text-danger">
          Query failed — the memory service may still be warming up. Try again.
        </p>
      ) : answer ? (
        <>
          <p className="animate-fade-in-up max-w-[65ch] text-[15px] leading-[1.65] text-foreground">
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

          {answeredAt ? (
            <div className="mt-3 text-right text-[11px] tabular-nums text-text-muted">
              answered {answeredAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
