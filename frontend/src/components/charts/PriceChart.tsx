"use client";

import * as React from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PriceBar } from "@/types";
import type { ChartMarker } from "@/utils/markers";
import { formatCurrency, formatDate } from "@/utils/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import {
  MarkerDot,
  NewsMarkerOverlay,
  type SelectedMarker,
} from "./NewsMarkerOverlay";

const CHART_HEIGHT = 320;

export interface PriceChartProps {
  ticker: string;
  bars: PriceBar[];
  /** Citation markers pinned to the price line (from the current answer). */
  markers?: ChartMarker[];
  /** Reveal beat — markers drop in only after this flips true. */
  revealMarkers?: boolean;
  isLoading?: boolean;
  isError?: boolean;
}

/** Themed tooltip matching the design system (no default recharts chrome). */
function PriceTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
  if (!active || !payload?.length) return null;
  const bar = (payload[0] as { payload: PriceBar }).payload;
  return (
    <div className="rounded-lg border border-border bg-surface-raised px-3 py-2 shadow-elevated">
      <div className="text-[11px] uppercase tracking-wide text-text-muted">{formatDate(bar.t)}</div>
      <div className="mt-0.5 text-sm font-semibold tabular-nums text-foreground">
        {formatCurrency(bar.c)}
      </div>
    </div>
  );
}

/**
 * Price line chart with news/citation markers landing on the line.
 * The marker layer (SVG dots via ReferenceDot + an HTML floating card) is owned
 * by NewsMarkerOverlay; this component wires it to the recharts x/y scales.
 */
export function PriceChart({
  ticker,
  bars,
  markers = [],
  revealMarkers = false,
  isLoading = false,
  isError = false,
}: PriceChartProps) {
  const [selected, setSelected] = React.useState<SelectedMarker | null>(null);

  // Drop the floating card whenever the underlying answer/markers change.
  React.useEffect(() => {
    setSelected(null);
  }, [markers]);

  const last = bars.at(-1)?.c;
  const first = bars.at(0)?.c;
  const delta = last != null && first != null && first !== 0 ? (last - first) / first : null;

  return (
    <Card className="shadow-elevated">
      <CardHeader className="flex-row items-baseline justify-between space-y-0">
        <CardTitle className="text-[15px] font-medium uppercase tracking-wide text-text-muted">
          {ticker} · Price
        </CardTitle>
        {last != null ? (
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-semibold tabular-nums text-foreground">
              {formatCurrency(last)}
            </span>
            {delta != null ? (
              <span
                className={`text-sm font-medium tabular-nums ${
                  delta >= 0 ? "text-primary" : "text-danger"
                }`}
              >
                {delta >= 0 ? "▲" : "▼"} {(Math.abs(delta) * 100).toFixed(2)}%
              </span>
            ) : null}
          </div>
        ) : null}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="shimmer h-[320px] w-full rounded-lg" />
        ) : isError ? (
          <div className="flex h-[320px] items-center justify-center text-sm text-text-muted">
            Couldn&apos;t load price data. Try another range.
          </div>
        ) : bars.length === 0 ? (
          <div className="flex h-[320px] items-center justify-center text-sm text-text-muted">
            No price data for this range.
          </div>
        ) : (
          <div className="relative" style={{ height: CHART_HEIGHT }}>
            <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
              <LineChart data={bars} margin={{ top: 12, right: 12, bottom: 4, left: 4 }}>
                <CartesianGrid stroke="hsl(var(--border))" strokeOpacity={0.4} vertical={false} />
                <XAxis dataKey="t" hide />
                <YAxis
                  domain={["auto", "auto"]}
                  width={52}
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => formatCurrency(v).replace(/\.00$/, "")}
                />
                <Tooltip
                  content={<PriceTooltip />}
                  cursor={{ stroke: "hsl(var(--border))", strokeWidth: 1 }}
                />
                <Line
                  type="monotone"
                  dataKey="c"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: "hsl(var(--primary))", stroke: "hsl(var(--background))" }}
                  isAnimationActive={false}
                />
                {markers.map((m, i) => (
                  <ReferenceDot
                    key={m.citation.id}
                    x={m.t}
                    y={m.y}
                    r={0}
                    isFront
                    ifOverflow="extendDomain"
                    shape={(props) => (
                      <MarkerDot
                        cx={(props as { cx?: number }).cx}
                        cy={(props as { cy?: number }).cy}
                        marker={m}
                        index={i}
                        reveal={revealMarkers}
                        onSelect={setSelected}
                      />
                    )}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            <NewsMarkerOverlay
              selected={selected}
              containerHeight={CHART_HEIGHT}
              onClose={() => setSelected(null)}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
