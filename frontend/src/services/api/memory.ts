import { apiClient } from "./client";
import { API_ROUTES } from "@/constants";
import type { ReflectionRequest } from "@/types";

/**
 * Memory feedback API module.
 * Wraps POST /memory/reflection — user 👍/👎 + optional correction on an answer.
 *
 * The endpoint may return 501 until the parallel reflection PR lands; callers
 * (see useReflection) degrade gracefully rather than surfacing an error toast.
 * The wire contract is snake_case; we map from the camelCase DTO here.
 */
export async function postReflection(request: ReflectionRequest): Promise<void> {
  await apiClient.post(API_ROUTES.memoryReflection, {
    ticker: request.ticker,
    question: request.question,
    feedback_text: request.feedbackText,
    helpful: request.helpful,
  });
}
