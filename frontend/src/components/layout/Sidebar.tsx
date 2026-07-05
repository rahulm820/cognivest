"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, BrainCircuit, Search, TrendingUp, Eraser } from "lucide-react";
import { cn } from "@/utils/cn";

const LIFECYCLE = [
  { icon: BrainCircuit, label: "Remember" },
  { icon: Search, label: "Recall" },
  { icon: TrendingUp, label: "Improve" },
  { icon: Eraser, label: "Forget" },
] as const;

/** Primary navigation sidebar + a quiet lifecycle legend pinned at the bottom. */
export function Sidebar() {
  const pathname = usePathname();
  const active = pathname === "/dashboard" || pathname === "/";

  return (
    <aside className="hidden w-56 shrink-0 flex-col justify-between border-r border-border bg-surface p-4 md:flex">
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

      <div className="mt-6">
        <div className="mb-2 px-1 text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted">
          Memory lifecycle
        </div>
        <ul className="space-y-0.5">
          {LIFECYCLE.map(({ icon: Icon, label }) => (
            <li
              key={label}
              className="flex items-center gap-2 px-1 py-1 text-[12px] text-text-muted"
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
