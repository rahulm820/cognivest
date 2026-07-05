"use client";

import * as React from "react";
import type { Citation } from "@/types";
import { useUiStore } from "@/store";
import { formatDate } from "@/utils/format";
import { cn } from "@/utils/cn";

export interface CitationChipProps {
  citation: Citation;
  /** Reveal index — drives the 60ms stagger of the entrance animation. */
  index?: number;
  /** When false, the chip is hidden (pre-reveal in the choreography). */
  revealed?: boolean;
}

/** Derive a favicon URL from a citation's source host (Google's s2 service). */
function faviconFor(url: string | null): string | null {
  if (!url) return null;
  try {
    const host = new URL(url).hostname;
    return `https://www.google.com/s2/favicons?domain=${host}&sz=32`;
  } catch {
    return null;
  }
}

/**
 * Clickable source citation chip: favicon-dot + title + date.
 * Hover lifts the chip and pulses its correlated chart marker via the shared
 * `hoveredCitationId` store slice (and vice versa — the linkage is bidirectional).
 * A citation with a null URL renders without a link affordance, muted.
 */
export function CitationChip({ citation, index = 0, revealed = true }: CitationChipProps) {
  const hoveredId = useUiStore((s) => s.hoveredCitationId);
  const setHovered = useUiStore((s) => s.setHoveredCitationId);
  const isHovered = hoveredId === citation.id;
  const hasLink = Boolean(citation.url);
  const favicon = faviconFor(citation.url);
  const [imgOk, setImgOk] = React.useState(true);

  const dateLabel = formatDate(citation.publishedAt);

  const inner = (
    <>
      <span
        className={cn(
          "flex h-4 w-4 shrink-0 items-center justify-center overflow-hidden rounded-full",
          !favicon || !imgOk ? "bg-primary/70" : "bg-surface-raised",
        )}
        aria-hidden
      >
        {favicon && imgOk ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={favicon}
            alt=""
            width={16}
            height={16}
            className="h-4 w-4"
            onError={() => setImgOk(false)}
          />
        ) : null}
      </span>
      <span className="truncate">{citation.title}</span>
      {dateLabel ? (
        <span className="shrink-0 tabular-nums text-text-muted">· {dateLabel}</span>
      ) : null}
    </>
  );

  const className = cn(
    "group inline-flex max-w-full items-center gap-2 rounded-full border px-3 py-1.5 text-[13px]",
    "transition-all duration-200 ease-out",
    revealed ? "animate-fade-in-up" : "pointer-events-none opacity-0",
    isHovered
      ? "-translate-y-0.5 border-primary/60 bg-surface-raised text-foreground shadow-marker-glow"
      : "border-border bg-surface text-foreground/90",
    hasLink ? "cursor-pointer hover:-translate-y-0.5 hover:border-primary/60" : "cursor-default",
    !hasLink && "text-text-muted",
  );

  const style = revealed ? { animationDelay: `${index * 60}ms` } : undefined;

  const handlers = {
    onMouseEnter: () => setHovered(citation.id),
    onMouseLeave: () => setHovered(null),
    onFocus: () => setHovered(citation.id),
    onBlur: () => setHovered(null),
  };

  if (hasLink) {
    return (
      <a
        href={citation.url ?? undefined}
        target="_blank"
        rel="noopener noreferrer"
        className={className}
        style={style}
        title={citation.title}
        {...handlers}
      >
        {inner}
      </a>
    );
  }

  return (
    <span className={className} style={style} title={citation.title} {...handlers}>
      {inner}
    </span>
  );
}
