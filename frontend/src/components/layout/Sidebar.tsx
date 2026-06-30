import Link from "next/link";
import { LayoutDashboard, ShieldCheck } from "lucide-react";

/** Primary navigation sidebar. */
export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r bg-card p-4 md:block">
      <nav className="flex flex-col gap-1 text-sm">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 rounded-md px-3 py-2 hover:bg-accent"
        >
          <LayoutDashboard className="h-4 w-4" />
          Dashboard
        </Link>
        <Link
          href="/admin"
          className="flex items-center gap-2 rounded-md px-3 py-2 hover:bg-accent"
        >
          <ShieldCheck className="h-4 w-4" />
          Ingestion Health
        </Link>
      </nav>
    </aside>
  );
}
