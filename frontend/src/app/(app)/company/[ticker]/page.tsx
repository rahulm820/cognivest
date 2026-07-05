import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CompanyWorkspace } from "@/features/company-query";
import { SEEDED_TICKERS } from "@/constants";

export function generateMetadata({ params }: { params: { ticker: string } }): Metadata {
  return { title: params.ticker.toUpperCase() };
}

/**
 * Company detail page — the choreographed demo surface (ARCHITECTURE.md §3.3):
 * price chart with citation markers above, NL query below, Agent Memory rail
 * alongside. All state + choreography lives in CompanyWorkspace. Unknown tickers
 * (outside the seeded watchlist) 404 into the styled not-found page.
 */
export default function CompanyPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  const known = SEEDED_TICKERS.some((c) => c.ticker === ticker);
  if (!known) notFound();
  return <CompanyWorkspace ticker={ticker} />;
}
