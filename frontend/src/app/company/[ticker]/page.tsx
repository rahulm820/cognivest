import { CompanyWorkspace } from "@/features/company-query";

/**
 * Company detail page — the choreographed demo surface (ARCHITECTURE.md §3.3):
 * price chart with citation markers above, NL query below, Agent Memory rail
 * alongside. All state + choreography lives in CompanyWorkspace.
 */
export default function CompanyPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  return <CompanyWorkspace ticker={ticker} />;
}
