"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard } from "lucide-react";
import { cn } from "@/utils/cn";

/** Primary navigation sidebar. */
export function Sidebar() {
  const pathname = usePathname();
  const active = pathname === "/dashboard" || pathname === "/";

  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-surface p-4 md:block">
      <nav className="flex flex-col gap-1 text-sm">
        <Link
          href="/dashboard"
          className={cn(
            "flex items-center gap-2 rounded-lg px-3 py-2 transition-colors",
            active
              ? "bg-primary/10 font-medium text-primary"
              : "text-text-muted hover:bg-surface-raised hover:text-foreground",
          )}
        >
          <LayoutDashboard className="h-4 w-4" />
          Watchlist
        </Link>
      </nav>
    </aside>
  );
}
