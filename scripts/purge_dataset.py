#!/usr/bin/env python3
"""Purge a Cognee dataset for a ticker (admin only).

CLI equivalent of DELETE /memory/delete. Removes a company's Cognee dataset
(company_{ticker}) entirely, or a date-bounded slice of it, going through the
single Cognee seam (memory_service -> cognee_client). Never imports the Cognee
SDK directly; never crosses datasets.

Scaffold phase: body is a stub marked ``# TODO(phase-3)``.
See scripts/README.md, docs/memory-architecture.md, docs/api.md.
"""

from __future__ import annotations

import argparse
import sys

SCOPES = ("all", "range")


def purge(ticker: str, scope: str, date_from: str | None, date_to: str | None) -> None:
    """Purge memory for ``company_{ticker}``.

    Args:
        ticker: ticker symbol; dataset is f"company_{ticker}".
        scope: "all" to delete the whole dataset, "range" for a date-bounded slice.
        date_from / date_to: bounds required when scope == "range".

    TODO(phase-3): call memory_service purge (-> cognee_client delete), scoped to
    the single dataset. For scope == "range", pass the date filter. Admin-only.
    """
    raise NotImplementedError("TODO(phase-3): call memory_service purge via the Cognee seam")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge a Cognee dataset for a ticker (admin).")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL.")
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        default="all",
        help="'all' = whole dataset; 'range' = date-bounded slice (default: %(default)s).",
    )
    parser.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD) for --scope range.")
    parser.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD) for --scope range.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm the destructive purge (required to actually run).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ticker = args.ticker.upper()

    if args.scope == "range" and not (args.date_from and args.date_to):
        print("error: --scope range requires --from and --to", file=sys.stderr)
        return 2
    if not args.yes:
        print(
            f"refusing to purge company_{ticker} (scope={args.scope}) without --yes",
            file=sys.stderr,
        )
        return 2

    print(f"Purging company_{ticker} (scope={args.scope})...")
    purge(ticker=ticker, scope=args.scope, date_from=args.date_from, date_to=args.date_to)
    return 0


if __name__ == "__main__":
    sys.exit(main())
