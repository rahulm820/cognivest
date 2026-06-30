import Link from "next/link";
import { TickerSearch } from "@/components/common";

/** Top navigation bar with brand + ticker search. */
export function TopNav() {
  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-4">
      <Link href="/dashboard" className="text-base font-semibold">
        Cognivest
      </Link>
      <div className="w-64">
        <TickerSearch />
      </div>
    </header>
  );
}
