import { apiClient } from "./client";
import { API_ROUTES } from "@/constants";
import type { QueryRequest, QueryResponse } from "@/types";

/**
 * Company natural-language query API module.
 * Wraps POST /companies/{ticker}/query (backend → Cognee search → Claude answer).
 * TODO(phase-4): align request/response shapes with the live OpenAPI contract.
 */
export async function postCompanyQuery(
  ticker: string,
  request: QueryRequest,
): Promise<QueryResponse> {
  const { data } = await apiClient.post<QueryResponse>(API_ROUTES.companyQuery(ticker), request);
  return data;
}
