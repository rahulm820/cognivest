"use client";

import type { JobRun } from "@/types";

/**
 * Panel listing errors from failed ingestion jobs.
 * TODO(phase-6): expand into a paginated, filterable error log view.
 */
export function ErrorLogPanel({ jobs }: { jobs: JobRun[] }) {
  if (jobs.length === 0) return null;

  return (
    <div className="rounded-md border border-destructive/40 p-4">
      <h3 className="mb-2 text-sm font-semibold text-destructive">Errors</h3>
      <ul className="space-y-1 text-sm">
        {jobs.map((job) => (
          <li key={job.id}>
            <span className="font-medium">{job.ticker}</span> ({job.type}):{" "}
            {job.error ?? "Unknown error"}
          </li>
        ))}
      </ul>
    </div>
  );
}
