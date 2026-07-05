import { WatchlistGrid } from "@/features/watchlist";

/** Dashboard — seeded watchlist of companies (ARCHITECTURE.md §3.3). */
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Watchlist</h1>
        <p className="mt-1 text-[14px] text-text-muted">
          Per-company financial intelligence — pick a ticker to ask questions grounded in its
          price &amp; news.
        </p>
      </div>
      <WatchlistGrid />
    </div>
  );
}
