"use client";

import * as React from "react";
import { useUiStore } from "@/store";
import { formatDate } from "@/utils/format";
import { cn } from "@/utils/cn";
import type { ChartMarker } from "@/utils/markers";

/** A marker the user has clicked — carries pixel coords for the floating card. */
export interface SelectedMarker {
  marker: ChartMarker;
  cx: number;
  cy: number;
}

interface MarkerDotProps {
  /** Pixel coords injected by recharts' ReferenceDot `shape` callback. */
  cx?: number;
  cy?: number;
  marker: ChartMarker;
  index: number;
  /** Gate: markers only render (and drop in) after the reveal beat. */
  reveal: boolean;
  onSelect: (selected: SelectedMarker) => void;
}

/**
 * SVG marker dot rendered as a ReferenceDot `shape`. An emerald dot lands on the
 * price line and pulses twice, then settles. While its citation is hover-linked
 * (chip ⇄ marker, shared via `hoveredCitationId`) it enlarges and pulses
 * continuously — the "wow" linkage detail.
 */
export function MarkerDot({ cx, cy, marker, index, reveal, onSelect }: MarkerDotProps) {
  const hoveredId = useUiStore((s) => s.hoveredCitationId);
  const setHovered = useUiStore((s) => s.setHoveredCitationId);

  if (!reveal || cx == null || cy == null) return null;
  const isHovered = hoveredId === marker.citation.id;

  return (
    <g
      className="animate-marker-drop cursor-pointer"
      style={{ animationDelay: `${index * 70}ms` }}
      transform={`translate(${cx}, ${cy})`}
      onMouseEnter={() => setHovered(marker.citation.id)}
      onMouseLeave={() => setHovered(null)}
      onClick={() => onSelect({ marker, cx, cy })}
    >
      {/* pulse ring: two pulses then settle; continuous while hover-linked */}
      <circle
        r={5}
        fill="hsl(var(--primary))"
        className={isHovered ? "animate-pulse-ring-linked" : "animate-pulse-ring"}
        opacity={0.5}
      />
      {/* generous invisible hit area */}
      <circle r={12} fill="transparent" />
      {/* solid dot */}
      <circle
        r={isHovered ? 6 : 4.5}
        fill="hsl(var(--primary))"
        stroke="hsl(var(--background))"
        strokeWidth={2}
        style={{ transition: "r 150ms ease-out" }}
      />
    </g>
  );
}

/** Extract a readable host label from a citation URL, if any. */
function hostLabel(url: string | null): string | null {
  if (!url) return null;
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

export interface NewsMarkerOverlayProps {
  /** The currently-selected marker + its pixel coords, or null. */
  selected: SelectedMarker | null;
  /** Chart container height — used to flip the card above/below the dot. */
  containerHeight: number;
  onClose: () => void;
}

/**
 * Floating citation card shown when a chart marker is clicked. Rendered as an
 * absolutely-positioned HTML layer over the chart (coords come from the marker's
 * pixel position), so it reads crisply against the SVG line.
 */
export function NewsMarkerOverlay({ selected, containerHeight, onClose }: NewsMarkerOverlayProps) {
  if (!selected) return null;
  const { marker, cx, cy } = selected;
  const { citation } = marker;
  const host = hostLabel(citation.url);
  const flipUp = cy > containerHeight / 2;

  return (
    <div
      className="animate-fade-in-up absolute z-20 w-60"
      style={{
        left: Math.max(8, Math.min(cx - 120, 10_000)),
        top: flipUp ? cy - 12 : cy + 16,
        transform: flipUp ? "translateY(-100%)" : undefined,
      }}
      role="dialog"
    >
      <div className="rounded-xl border border-border bg-surface-raised p-3 shadow-elevated">
        <div className="mb-1.5 flex items-center justify-between gap-2">
          <span className="inline-flex items-center gap-1 rounded-full bg-primary/15 px-2 py-0.5 text-[11px] font-medium text-primary">
            cited in current answer
          </span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="text-text-muted transition-colors hover:text-foreground"
          >
            ✕
          </button>
        </div>
        <p className="text-[13px] font-medium leading-snug text-foreground">{citation.title}</p>
        <div className="mt-1.5 flex items-center gap-2 text-[11px] text-text-muted">
          {host ? <span className="truncate">{host}</span> : <span>source unavailable</span>}
          {citation.publishedAt ? (
            <span className="tabular-nums">· {formatDate(citation.publishedAt)}</span>
          ) : null}
        </div>
        {citation.url ? (
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "mt-2 inline-block text-[12px] font-medium text-primary",
              "transition-colors hover:text-primary-hover",
            )}
          >
            Open source →
          </a>
        ) : null}
      </div>
    </div>
  );
}
