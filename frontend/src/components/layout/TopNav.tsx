import Link from "next/link";
import { TickerSearch } from "@/components/common";

/** Top navigation bar with brand + ticker search. */
export function TopNav() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-surface px-4">
      <Link href="/dashboard" className="flex items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/15 text-primary">
          ◆
        </span>
        <span className="text-base font-semibold text-foreground">Cognivest</span>
      </Link>
      <div className="w-64">
        <TickerSearch />
      </div>
    </header>
  );
}
