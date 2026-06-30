#!/usr/bin/env python3
"""Enqueue a historical backfill for a ticker.

Schedules collector jobs (price + news) over a historical window onto the Celery
queues; cognify follows on its own queue. Idempotent: dedup runs before
cognee.add(), so re-running a backfill is safe.

Scaffold phase: body is a stub marked ``# TODO(phase-2)``.
See scripts/README.md and docs/backend.md.
"""

from __future__ import annotations

import argparse
import sys


def backfill(ticker: str, days: int, news: bool, price: bool) -> None:
    """Enqueue backfill jobs for ``ticker`` over the trailing ``days`` window.

    TODO(phase-2): resolve/validate the company, then enqueue price and/or news
    collector tasks for the window via the workers (Celery). Dedup runs inside
    each task before cognee.add(); cognify is enqueued separately. Memory stays
    scoped to f"company_{ticker}".
    """
    raise NotImplementedError("TODO(phase-2): enqueue backfill collector jobs")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill historical data for a ticker.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL.")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of trailing days to backfill (default: %(default)s).",
    )
    parser.add_argument("--no-news", action="store_true", help="Skip news/web backfill.")
    parser.add_argument("--no-price", action="store_true", help="Skip price backfill.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ticker = args.ticker.upper()
    print(f"Enqueuing backfill for {ticker} ({args.days}d)...")
    backfill(
        ticker=ticker,
        days=args.days,
        news=not args.no_news,
        price=not args.no_price,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
