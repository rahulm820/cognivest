"use client";

import { useJobRuns } from "@/hooks";
import { Badge, Spinner } from "@/components/ui";
import { formatDate } from "@/utils/format";
import type { JobRun } from "@/types";
import { ErrorLogPanel } from "./ErrorLogPanel";

const STATUS_VARIANT: Record<JobRun["status"], "success" | "secondary" | "destructive"> = {
  success: "success",
  running: "secondary",
  failed: "destructive",
};

/**
 * Admin ingestion job-run table (polls via useJobRuns).
 * TODO(phase-6): add per-ticker filtering + pagination.
 */
export function JobRunTable() {
  const { data, isLoading, isError } = useJobRuns();

  if (isLoading) return <Spinner />;
  if (isError) return <p className="text-sm text-destructive">Failed to load job runs.</p>;

  const jobs = data ?? [];

  return (
    <div className="space-y-4">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-muted-foreground">
            <th className="py-2">Ticker</th>
            <th className="py-2">Type</th>
            <th className="py-2">Status</th>
            <th className="py-2">Last run</th>
            <th className="py-2">Items</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} className="border-b">
              <td className="py-2 font-medium">{job.ticker}</td>
              <td className="py-2">{job.type}</td>
              <td className="py-2">
                <Badge variant={STATUS_VARIANT[job.status]}>{job.status}</Badge>
              </td>
              <td className="py-2">{formatDate(job.lastRun)}</td>
              <td className="py-2">{job.itemsIngested}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ErrorLogPanel jobs={jobs.filter((job) => job.status === "failed")} />
    </div>
  );
}
