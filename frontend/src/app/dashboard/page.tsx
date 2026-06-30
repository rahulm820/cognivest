import { AddTickerModal, WatchlistTable } from "@/features/watchlist";

/** Dashboard — watchlist of companies + add-ticker action (ARCHITECTURE.md §3.3). */
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <AddTickerModal />
      </div>
      <WatchlistTable />
    </div>
  );
}
