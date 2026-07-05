"use client";

import Link from "next/link";
import { Line, LineChart, ResponsiveContainer, YAxis } from "recharts";
import { useCompanyPrice } from "@/hooks";
import { formatCurrency, formatDate } from "@/utils/format";
import { cn } from "@/utils/cn";

export interface WatchlistCardProps {
  ticker: string;
  name: string;
  /** Entrance-stagger index (× 70ms). */
  index?: number;
}

const SPARK_RANGE = "3m";

/**
 * Dashboard company card: ticker + name + live price + % delta pill + last-close
 * date + a compact emerald sparkline (its own /price fetch). Hover glows the
 * border emerald and brightens the sparkline. Fully handles loading (shimmer),
 * error, and empty states — never a raw error or blank white.
 */
export function WatchlistCard({ ticker, name, index = 0 }: WatchlistCardProps) {
  const { data, isLoading, isError } = useCompanyPrice(ticker, SPARK_RANGE);
  const bars = data?.bars ?? [];

  const last = bars.at(-1)?.c;
  const first = bars.at(0)?.c;
  const lastDate = bars.at(-1)?.t;
  const delta = last != null && first != null && first !== 0 ? (last - first) / first : null;
  const up = (delta ?? 0) >= 0;

  return (
    <Link
      href={`/company/${ticker}`}
      style={{ animationDelay: `${index * 70}ms` }}
      className={cn(
        "animate-fade-in-up group flex flex-col gap-4 rounded-xl border border-border bg-surface p-5 shadow-elevated",
        "transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-primary/60 hover:shadow-glow-card",
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
          <div className="flex flex-col items-end gap-1">
            <div className="text-lg font-semibold tabular-nums text-foreground">
              {formatCurrency(last)}
            </div>
            {delta != null ? (
              <div
                className={cn(
                  "rounded-full px-2 py-0.5 text-[12px] font-medium tabular-nums",
                  up ? "bg-primary/10 text-primary" : "bg-destructive/10 text-danger",
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
          <div className="h-full opacity-80 transition-opacity duration-200 group-hover:opacity-100">
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
          </div>
        ) : (
          <div className="flex h-full items-center text-[12px] text-text-muted">no recent data</div>
        )}
      </div>

      {lastDate ? (
        <div className="text-[11px] text-text-muted">as of {formatDate(lastDate)}</div>
      ) : null}
    </Link>
  );
}
