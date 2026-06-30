#!/usr/bin/env python3
"""Seed a demo ticker into Postgres.

Inserts a demo company (and optionally a demo user) so the dashboard isn't empty
on first run. Goes through repositories (no inline SQL).

Scaffold phase: body is a stub marked ``# TODO(phase-1)``.
See scripts/README.md and docs/database.md.
"""

from __future__ import annotations

import argparse
import sys

DEFAULT_TICKER = "AAPL"
DEFAULT_NAME = "Apple Inc."


def seed(ticker: str, name: str) -> None:
    """Insert a demo company into Postgres via the company repository.

    TODO(phase-1): open a DB session, upsert the company (idempotent on the
    unique COMPANIES(ticker) index), and optionally enqueue an initial backfill.
    All access goes through repositories -- no inline SQL.
    """
    raise NotImplementedError("TODO(phase-1): seed demo company via repository")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed a demo ticker into Postgres.")
    parser.add_argument("--ticker", default=DEFAULT_TICKER, help="Ticker (default: %(default)s).")
    parser.add_argument("--name", default=DEFAULT_NAME, help="Company name (default: %(default)s).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ticker = args.ticker.upper()
    print(f"Seeding demo company {ticker} ({args.name})...")
    seed(ticker=ticker, name=args.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
