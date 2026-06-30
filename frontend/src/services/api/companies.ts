import { apiClient } from "./client";
import { API_ROUTES } from "@/constants";
import type { Company, PriceSeries } from "@/types";

/**
 * Companies / watchlist API module.
 * TODO(phase-5): wire to real backend responses once endpoints are live.
 */

/** GET /companies — list watchlisted companies. */
export async function getCompanies(): Promise<Company[]> {
  const { data } = await apiClient.get<Company[]>(API_ROUTES.companies);
  return data;
}

/** POST /companies — add a ticker to the watchlist. */
export async function addCompany(ticker: string): Promise<Company> {
  const { data } = await apiClient.post<Company>(API_ROUTES.companies, { ticker });
  return data;
}

/** GET /companies/{ticker}/price?range=... — price series for a ticker. */
export async function getPriceSeries(ticker: string, range: string): Promise<PriceSeries> {
  const { data } = await apiClient.get<PriceSeries>(API_ROUTES.companyPrice(ticker), {
    params: { range },
  });
  return data;
}

/** DELETE /companies/{ticker} — remove from watchlist. */
export async function deleteCompany(ticker: string): Promise<void> {
  await apiClient.delete(API_ROUTES.company(ticker));
}
