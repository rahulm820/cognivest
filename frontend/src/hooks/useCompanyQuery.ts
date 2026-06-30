"use client";

import { useMutation } from "@tanstack/react-query";
import { postCompanyQuery } from "@/services/api";
import type { QueryRequest, QueryResponse } from "@/types";

/**
 * Natural-language company query mutation (ARCHITECTURE.md §3.3 company detail).
 * Mutations surface errors directly (no auto-retry).
 * TODO(phase-4): add result caching / query-log integration.
 */
export function useCompanyQuery(ticker: string) {
  return useMutation<QueryResponse, unknown, QueryRequest>({
    mutationFn: (request: QueryRequest) => postCompanyQuery(ticker, request),
  });
}
