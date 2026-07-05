import type { Metadata } from "next";
import { WatchlistGrid } from "@/features/watchlist";
import { AskPanel } from "@/features/watchlist/AskPanel";

export const metadata: Metadata = { title: "Watchlist" };

/** Dashboard — seeded watchlist of companies (ARCHITECTURE.md §3.3). */
export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Watchlist</h1>
          <p className="mt-1 text-[14px] text-text-muted">
            Pick a ticker to ask questions grounded in its price &amp; news.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-1.5">
          <span className="relative flex h-2 w-2" aria-hidden>
            <span className="animate-pulse-soft absolute inline-flex h-full w-full rounded-full bg-primary" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
          </span>
          <span className="text-[13px] text-text-muted">
            <span className="font-medium text-foreground">3 companies</span> · knowledge graphs
            active
          </span>
        </div>
      </div>

      <WatchlistGrid />

      <AskPanel />
    </div>
  );
}
