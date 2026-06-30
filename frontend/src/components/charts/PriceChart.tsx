"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PriceBar } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";

export interface PriceChartProps {
  ticker: string;
  bars: PriceBar[];
}

/**
 * Price chart placeholder (Recharts line; candlestick TODO).
 * TODO(phase-5): swap to candlestick + integrate NewsMarkerOverlay.
 */
export function PriceChart({ ticker, bars }: PriceChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{ticker} — Price</CardTitle>
      </CardHeader>
      <CardContent>
        {bars.length === 0 ? (
          <p className="text-sm text-muted-foreground">No price data.</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={bars}>
              <XAxis dataKey="t" hide />
              <YAxis domain={["auto", "auto"]} width={48} />
              <Tooltip />
              <Line type="monotone" dataKey="c" stroke="hsl(var(--primary))" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
