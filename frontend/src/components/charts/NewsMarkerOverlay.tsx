"use client";

import type { Citation } from "@/types";

export interface NewsMarkerOverlayProps {
  /** News/citation markers to correlate with price points on the chart. */
  markers: Citation[];
}

/**
 * Overlay of news markers correlated to chart dates (ARCHITECTURE.md §3.3).
 * TODO(phase-5): render markers positioned against the PriceChart x-axis.
 */
export function NewsMarkerOverlay({ markers }: NewsMarkerOverlayProps) {
  return (
    <div className="text-xs text-muted-foreground" data-marker-count={markers.length}>
      {/* TODO(phase-5): position {markers.length} news markers over the price chart. */}
      News marker overlay placeholder
    </div>
  );
}
