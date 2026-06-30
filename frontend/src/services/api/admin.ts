import { apiClient } from "./client";
import { API_ROUTES } from "@/constants";
import type { JobRun } from "@/types";

/**
 * Admin / ingestion-health API module.
 * TODO(phase-6): wire to real /admin/jobs payload.
 */

/** GET /admin/jobs — ingestion job runs per company (admin only). */
export async function getJobRuns(): Promise<JobRun[]> {
  const { data } = await apiClient.get<{ jobs: JobRun[] }>(API_ROUTES.adminJobs);
  return data.jobs;
}
