"use client";

import type { Citation } from "@/types";
import { Badge } from "@/components/ui";

export interface CitationChipProps {
  citation: Citation;
  /** Scroll-link to the correlated chart marker (ARCHITECTURE.md §3.3). */
  onClick?: (citation: Citation) => void;
}

/** Clickable source citation chip. */
export function CitationChip({ citation, onClick }: CitationChipProps) {
  return (
    <button type="button" onClick={() => onClick?.(citation)} className="inline-flex">
      <Badge variant="outline" className="cursor-pointer hover:bg-accent">
        {/* TODO(phase-4): link to chart marker for citation.publishedAt */}
        {citation.title}
      </Badge>
    </button>
  );
}
