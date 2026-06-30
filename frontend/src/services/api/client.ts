import axios, { type AxiosError, type AxiosInstance } from "axios";

/**
 * Centralized axios instance — the single seam for all backend HTTP access.
 * Components MUST NOT call fetch/axios directly (CLAUDE.md §5).
 *
 * Responsibilities:
 *  - baseURL from NEXT_PUBLIC_API_BASE_URL
 *  - auth header injection (placeholder until auth lands)
 *  - retry-on-401-refresh (placeholder)
 *  - error normalization into a consistent shape
 */

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface NormalizedApiError {
  code: string;
  message: string;
  status?: number;
  detail?: unknown;
}

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

// --- Request interceptor: attach auth token -------------------------------
apiClient.interceptors.request.use((config) => {
  // TODO(phase-1): read the access token from the auth store / cookie and attach it.
  // const token = getAccessToken();
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- Response interceptor: normalize errors + refresh-on-401 --------------
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // TODO(phase-1): on 401, attempt a single token refresh via auth.refresh()
    // and replay the original request before rejecting.
    return Promise.reject(normalizeError(error));
  },
);

/** Collapse any axios/unknown error into a consistent NormalizedApiError. */
export function normalizeError(error: unknown): NormalizedApiError {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { error?: Partial<NormalizedApiError> } | undefined;
    return {
      code: data?.error?.code ?? error.code ?? "unknown_error",
      message: data?.error?.message ?? error.message ?? "Unexpected error",
      status: error.response?.status,
      detail: data?.error?.detail,
    };
  }
  return {
    code: "unknown_error",
    message: error instanceof Error ? error.message : "Unexpected error",
  };
}
