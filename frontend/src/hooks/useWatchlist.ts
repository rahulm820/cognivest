"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addCompany, deleteCompany, getCompanies } from "@/services/api";
import { QUERY_KEYS } from "@/constants";
import type { Company } from "@/types";

/**
 * Watchlist server-state hooks (ARCHITECTURE.md §3.6).
 * TODO(phase-5): refine staleTime, optimistic updates, and error toasts.
 */

/** Fetch the watchlisted companies. */
export function useWatchlist() {
  return useQuery<Company[]>({
    queryKey: QUERY_KEYS.watchlist,
    queryFn: getCompanies,
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
