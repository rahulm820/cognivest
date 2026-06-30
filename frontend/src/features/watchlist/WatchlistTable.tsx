"use client";

import Link from "next/link";
import { useWatchlist } from "@/hooks";
import { Spinner } from "@/components/ui";
import { IngestionHealthBadge } from "./IngestionHealthBadge";

/**
 * Watchlist table — lists companies with last price + ingestion health.
 * TODO(phase-5): add filter text, sorting, and row-level actions.
 */
export function WatchlistTable() {
  const { data, isLoading, isError } = useWatchlist();

  if (isLoading) return <Spinner />;
  if (isError) return <p className="text-sm text-destructive">Failed to load watchlist.</p>;

  const companies = data ?? [];

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left text-muted-foreground">
          <th className="py-2">Ticker</th>
          <th className="py-2">Name</th>
          <th className="py-2">Status</th>
        </tr>
      </thead>
      <tbody>
        {companies.length === 0 ? (
          <tr>
            <td colSpan={3} className="py-4 text-muted-foreground">
              No companies yet. Add a ticker to get started.
            </td>
          </tr>
        ) : (
          companies.map((company) => (
            <tr key={company.id} className="border-b hover:bg-accent">
              <td className="py-2 font-medium">
                <Link href={`/company/${company.ticker}`}>{company.ticker}</Link>
              </td>
              <td className="py-2">{company.name}</td>
              <td className="py-2">
                <IngestionHealthBadge status={company.status} />
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
