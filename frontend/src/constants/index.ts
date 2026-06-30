/**
 * App-wide constants: API route paths, React Query cache keys, and selectable ranges.
 */

/** Backend REST route builders (relative to NEXT_PUBLIC_API_BASE_URL). */
export const API_ROUTES = {
  login: "/auth/login",
  refresh: "/auth/refresh",
  companies: "/companies",
  company: (ticker: string) => `/companies/${ticker}`,
  companyPrice: (ticker: string) => `/companies/${ticker}/price`,
  companyQuery: (ticker: string) => `/companies/${ticker}/query`,
  adminJobs: "/admin/jobs",
} as const;

/** TanStack Query cache key factories — keep keys centralized for invalidation. */
export const QUERY_KEYS = {
  watchlist: ["watchlist"] as const,
  companyPrice: (ticker: string, range: string) => ["company", ticker, "price", range] as const,
  jobRuns: ["admin", "jobRuns"] as const,
} as const;

/** Selectable price-chart ranges shown in the DateRangePicker. */
export const PRICE_RANGES = ["1d", "5d", "1m", "3m", "6m", "1y", "5y"] as const;
export type PriceRange = (typeof PRICE_RANGES)[number];

export const DEFAULT_PRICE_RANGE: PriceRange = "1m";

/** Admin job-run polling interval (ms). See ARCHITECTURE.md §3.3 (admin screen). */
export const JOB_RUNS_POLL_INTERVAL_MS = 10_000;
