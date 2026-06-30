import { apiClient } from "./client";
import { API_ROUTES } from "@/constants";
import type { AuthTokens } from "@/types";

/**
 * Auth API module — JWT login + refresh (ARCHITECTURE.md §9).
 * TODO(phase-1): persist/rotate tokens and integrate with the client interceptor.
 */

/** POST /auth/login — exchange credentials for an access/refresh token pair. */
export async function login(email: string, password: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>(API_ROUTES.login, { email, password });
  return data;
}

/** POST /auth/refresh — rotate the access token using a refresh token. */
export async function refresh(refreshToken: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>(API_ROUTES.refresh, { refreshToken });
  return data;
}
