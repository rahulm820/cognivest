"use client";

import { useQuery } from "@tanstack/react-query";
import { getPriceSeries } from "@/services/api";
import { QUERY_KEYS } from "@/constants";
import type { PriceSeries } from "@/types";

/**
 * Price-series server-state hook for the company detail chart.
 * TODO(phase-5): tune staleTime/refetch behavior per range.
 */
export function useCompanyPrice(ticker: string, range: string) {
  return useQuery<PriceSeries>({
    queryKey: QUERY_KEYS.companyPrice(ticker, range),
    queryFn: () => getPriceSeries(ticker, range),
    enabled: Boolean(ticker),
  });
}
