"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addCompany, deleteCompany } from "@/services/api";
import { QUERY_KEYS, SEEDED_TICKERS } from "@/constants";
import type { Company } from "@/types";

/**
 * Watchlist server-state hooks (ARCHITECTURE.md §3.6).
 * TODO(phase-5): refine staleTime, optimistic updates, and error toasts.
 */

/**
 * Fetch the watchlisted companies.
 *
 * `GET /companies` currently returns 501, so the demo resolves the hardcoded
 * seeded watchlist (AAPL / MSFT / TSLA from `make seed`) instead of hitting the
 * live endpoint. Kept as a TanStack query so consumers (loading/error states)
 * are unchanged when the endpoint lands and `queryFn` swaps back to
 * `getCompanies`.
 */
export function useWatchlist() {
  return useQuery<Company[]>({
    queryKey: QUERY_KEYS.watchlist,
    queryFn: async () =>
      SEEDED_TICKERS.map((c) => ({
        id: c.ticker,
        ticker: c.ticker,
        name: c.name,
        status: "active" as const,
        createdAt: "",
      })),
    staleTime: Infinity,
  });
}

/** Add a ticker to the watchlist, invalidating the list on success. */
export function useAddTicker() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ticker: string) => addCompany(ticker),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.watchlist });
    },
  });
}

/** Remove a ticker from the watchlist. */
export function useRemoveTicker() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ticker: string) => deleteCompany(ticker),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.watchlist });
    },
  });
}
