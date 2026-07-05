import type { Citation, PriceBar } from "@/types";

/** A citation pinned to the price line at the nearest available bar. */
export interface ChartMarker {
  citation: Citation;
  /** The `t` value of the snapped bar — matches the chart's categorical x-axis. */
  t: string;
  /** Close price at the snapped bar — the marker's y position on the line. */
  y: number;
}

/**
 * Snap each citation with a `publishedAt` to the nearest price bar by timestamp.
 *
 * Recharts' categorical x-axis (`dataKey="t"`) only resolves reference points at
 * exact category values, so a raw `publishedAt` won't line up — we pin it to the
 * closest bar we actually have. Citations without a date, or whose date falls
 * outside the loaded window (beyond one bar's spacing), are dropped.
 */
export function buildChartMarkers(citations: Citation[], bars: PriceBar[]): ChartMarker[] {
  if (bars.length === 0) return [];

  const times = bars.map((b) => new Date(b.t).getTime());
  const first = times[0]!;
  const last = times[times.length - 1]!;
  // Allow a citation to snap if it's within the window, plus a one-bar grace band.
  const grace = bars.length > 1 ? (last - first) / (bars.length - 1) : 1000 * 60 * 60 * 24;

  const markers: ChartMarker[] = [];
  const usedT = new Set<string>();

  for (const citation of citations) {
    if (!citation.publishedAt) continue;
    const target = new Date(citation.publishedAt).getTime();
    if (Number.isNaN(target)) continue;
    if (target < first - grace || target > last + grace) continue;

    let bestIdx = 0;
    let bestDist = Infinity;
    for (let i = 0; i < times.length; i += 1) {
      const dist = Math.abs(times[i]! - target);
      if (dist < bestDist) {
        bestDist = dist;
        bestIdx = i;
      }
    }

    const bar = bars[bestIdx];
    if (!bar) continue;
    // Nudge collisions to a neighbouring bar so stacked citations stay visible.
    const next = bars[bestIdx + 1];
    const t = usedT.has(bar.t) && next ? next.t : bar.t;
    usedT.add(t);

    markers.push({ citation, t, y: bar.c });
  }

  return markers;
}
