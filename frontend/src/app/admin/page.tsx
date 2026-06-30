import { JobRunTable } from "@/features/ingestion-status";

/**
 * Admin / ingestion-health screen.
 * The JobRunTable polls on an interval (ARCHITECTURE.md §3.3 — refetchInterval).
 */
export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Ingestion Health</h1>
        <p className="text-sm text-muted-foreground">Auto-refreshes every 10s.</p>
      </div>
      <JobRunTable />
    </div>
  );
}
