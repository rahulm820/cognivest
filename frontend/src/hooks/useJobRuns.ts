"use client";

import { useQuery } from "@tanstack/react-query";
import { getJobRuns } from "@/services/api";
import { JOB_RUNS_POLL_INTERVAL_MS, QUERY_KEYS } from "@/constants";
import type { JobRun } from "@/types";

/**
 * Admin ingestion-health hook — polls on an interval (ARCHITECTURE.md §3.3).
 * TODO(phase-6): pause polling when the tab is hidden.
 */
export function useJobRuns() {
  return useQuery<JobRun[]>({
    queryKey: QUERY_KEYS.jobRuns,
    queryFn: getJobRuns,
    refetchInterval: JOB_RUNS_POLL_INTERVAL_MS,
  });
}
