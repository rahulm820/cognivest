import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Not found" };

/** Global 404 — one calm card, chrome-free, pointing back to the watchlist. */
export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md rounded-xl border border-border bg-surface p-8 text-center shadow-elevated">
        <span
          className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15 text-lg text-primary"
          aria-hidden
        >
          ◆
        </span>
        <h1 className="mt-4 text-xl font-semibold text-foreground">
          This ticker isn&apos;t in the watchlist
        </h1>
        <p className="mt-2 text-[14px] leading-relaxed text-text-muted">
          Nothing lives at this address. The demo watchlist tracks AAPL, MSFT and TSLA — each with
          its own knowledge graph.
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-primary px-5 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover"
        >
          Back to watchlist
        </Link>
      </div>
    </main>
  );
}
