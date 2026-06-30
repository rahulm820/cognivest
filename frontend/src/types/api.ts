/**
 * API contract types — hand-mirrored from the backend Pydantic schemas
 * (see ARCHITECTURE.md §4.4 / §7).
 *
 * TODO(phase-1): replace this file with OpenAPI-generated types once the backend
 * OpenAPI spec is the source of truth (`openapi-typescript` from /api/v1/openapi.json).
 */

/** A watchlisted company / ticker. Mirrors the COMPANIES table. */
export interface Company {
  id: string;
  ticker: string;
  name: string;
  /** Ingestion/backfill status surfaced to the dashboard. */
  status: "backfilling" | "active" | "error";
  lastPrice?: number;
  lastIngestedAt?: string;
  createdAt: string;
}

/** A single OHLCV price bar. Field names mirror the backend's compact payload. */
export interface PriceBar {
  /** ISO date/time of the bar. */
  t: string;
  /** Open. */
  o: number;
  /** High. */
  h: number;
  /** Low. */
  l: number;
  /** Close. */
  c: number;
  /** Volume. */
  v: number;
}

/** Price series response for a ticker over a range. */
export interface PriceSeries {
  ticker: string;
  range: string;
  bars: PriceBar[];
}

/** Inclusive from/to date range used for query filtering and chart windows. */
export interface DateRange {
  /** ISO date (YYYY-MM-DD). */
  from: string;
  /** ISO date (YYYY-MM-DD). */
  to: string;
}

/** A natural-language company query request. */
export interface QueryRequest {
  question: string;
  dateRange?: DateRange;
}

/** A source citation attached to an answer. */
export interface Citation {
  id: string;
  title: string;
  url: string;
  publishedAt: string;
}

/** Minimal graph snippet returned alongside an answer. */
export interface GraphSnippet {
  nodes: Array<{ id: string; label: string }>;
  edges: Array<{ from: string; to: string; label: string }>;
}

/** Answer to a company query, grounded in cited Cognee retrieval results. */
export interface QueryResponse {
  answer: string;
  citations: Citation[];
  graphSnippet?: GraphSnippet;
}

/** An ingestion job run, surfaced on the admin screen. */
export interface JobRun {
  id: string;
  ticker: string;
  type: "price" | "news" | "cognify";
  status: "success" | "running" | "failed";
  lastRun: string;
  itemsIngested: number;
  error?: string | null;
}

/** Authenticated application user. */
export interface User {
  id: string;
  email: string;
  role: "user" | "admin";
}

/** Auth token pair returned by login/refresh. */
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}
