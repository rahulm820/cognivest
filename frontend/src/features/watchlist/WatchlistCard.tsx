"use client";

import Link from "next/link";
import { Line, LineChart, ResponsiveContainer, YAxis } from "recharts";
import { useCompanyPrice } from "@/hooks";
import { formatCurrency } from "@/utils/format";
import { cn } from "@/utils/cn";

export interface WatchlistCardProps {
  ticker: string;
  name: string;
}

const SPARK_RANGE = "3m";

/**
 * Dashboard company card: ticker + name + live price + % delta + a compact
 * emerald sparkline (its own /price fetch). Fully handles loading (shimmer),
 * error, and empty states — never a raw error or blank white.
 */
export function WatchlistCard({ ticker, name }: WatchlistCardProps) {
  const { data, isLoading, isError } = useCompanyPrice(ticker, SPARK_RANGE);
  const bars = data?.bars ?? [];

  const last = bars.at(-1)?.c;
  const first = bars.at(0)?.c;
  const delta = last != null && first != null && first !== 0 ? (last - first) / first : null;
  const up = (delta ?? 0) >= 0;

  return (
    <Link
      href={`/company/${ticker}`}
      className={cn(
        "group flex flex-col gap-4 rounded-xl border border-border bg-surface p-5 shadow-elevated",
        "transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-primary/50",
      )}
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <div className="text-lg font-semibold text-foreground">{ticker}</div>
          <div className="truncate text-[13px] text-text-muted">{name}</div>
        </div>
        {isLoading ? (
          <div className="shimmer h-6 w-20 rounded" />
        ) : last != null ? (
          <div className="text-right">
            <div className="text-lg font-semibold tabular-nums text-foreground">
              {formatCurrency(last)}
            </div>
            {delta != null ? (
              <div
                className={cn(
                  "text-[13px] font-medium tabular-nums",
                  up ? "text-primary" : "text-danger",
                )}
              >
                {up ? "▲" : "▼"} {(Math.abs(delta) * 100).toFixed(2)}%
              </div>
            ) : null}
          </div>
        ) : (
          <div className="text-[13px] text-text-muted">—</div>
        )}
      </div>

      <div className="h-12">
        {isLoading ? (
          <div className="shimmer h-full w-full rounded" />
        ) : isError ? (
          <div className="flex h-full items-center text-[12px] text-text-muted">
            price unavailable
          </div>
        ) : bars.length > 1 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={bars} margin={{ top: 4, right: 2, bottom: 4, left: 2 }}>
              <YAxis domain={["dataMin", "dataMax"]} hide />
              <Line
                type="monotone"
                dataKey="c"
                stroke={up ? "hsl(var(--primary))" : "hsl(var(--destructive))"}
                strokeWidth={1.75}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center text-[12px] text-text-muted">
            no recent data
          </div>
        )}
      </div>
    </Link>
  );
}
