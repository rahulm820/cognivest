import Link from "next/link";

/**
 * In-app 404 — reached when a route under (app) calls notFound() (e.g. an
 * unknown ticker). Renders inside the app chrome (top nav + sidebar), unlike the
 * chrome-free root not-found used for wholly unknown URLs.
 */
export default function AppNotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
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
          The demo tracks AAPL, MSFT and TSLA — each with its own Cognee knowledge graph. Pick one
          from the watchlist to start asking.
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-primary px-5 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover"
        >
          Back to watchlist
        </Link>
      </div>
    </div>
  );
}
