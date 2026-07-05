"use client";

import { useMutation } from "@tanstack/react-query";
import { postReflection } from "@/services/api";
import { normalizeError } from "@/services/api";
import type { ReflectionRequest } from "@/types";

/** True when an error is the "endpoint not implemented yet" (501) signal. */
export function isNotImplemented(error: unknown): boolean {
  return normalizeError(error).status === 501;
}

/**
 * Answer-feedback mutation → POST /memory/reflection.
 * Mutations surface errors directly (no retry); the UI treats 501 specially
 * ("coming online shortly") and never shows a raw error toast.
 */
export function useReflection() {
  return useMutation<void, unknown, ReflectionRequest>({
    mutationFn: (request: ReflectionRequest) => postReflection(request),
  });
}
