"use client";

import type { QueryResponse } from "@/types";
import { Spinner } from "@/components/ui";
import { CitationChip } from "@/components/common";

export interface AnswerPanelProps {
  answer?: QueryResponse;
  isLoading?: boolean;
  isError?: boolean;
}

/**
 * Renders a query answer with citation chips.
 * TODO(phase-4): render graph snippet + scroll-link citations to chart markers.
 */
export function AnswerPanel({ answer, isLoading, isError }: AnswerPanelProps) {
  if (isLoading) return <Spinner />;
  if (isError) return <p className="text-sm text-destructive">Query failed. Try again.</p>;
  if (!answer) return null;

  return (
    <div className="space-y-2 rounded-md border p-4">
      <p className="text-sm">{answer.answer}</p>
      {answer.citations.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {answer.citations.map((citation) => (
            <CitationChip key={citation.id} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
