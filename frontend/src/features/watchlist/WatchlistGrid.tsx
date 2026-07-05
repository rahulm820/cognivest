"use client";

import { SEEDED_TICKERS } from "@/constants";
import { WatchlistCard } from "./WatchlistCard";

/**
 * Grid of seeded watchlist cards (AAPL / MSFT / TSLA).
 * `GET /companies` is 501, so the list is the hardcoded seeded set; each card
 * pulls its own live /price series.
 */
export function WatchlistGrid() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {SEEDED_TICKERS.map((c, i) => (
        <WatchlistCard key={c.ticker} ticker={c.ticker} name={c.name} index={i} />
      ))}
    </div>
  );
}
