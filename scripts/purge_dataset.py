#!/usr/bin/env python3
"""Forget a ticker's Cognee memory — the lifecycle counterpart to backfill (#9).

CLI equivalent of ``DELETE /api/v1/memory/delete``. Goes through the single Cognee
seam (memory_service -> cognee_client); never imports the Cognee SDK directly, never
crosses datasets.

Two modes, both honest about Cognee 1.2.2's real capability — it can only forget a
WHOLE dataset (there is no per-item / date-sliced delete, spike CONTRADICTION #2):

  * full purge (default): ``forget(company_{ticker})`` + clear the dedup ledger.
    The dataset is left empty.
  * staleness purge (``--older-than-days N``): forget the whole dataset + clear the
    ledger, then RE-BACKFILL only the last N days. Items that have aged out of the
    collectors' N-day window do not come back; recent ones are rebuilt. This is a
    rebuild-from-current-sources, not an in-place slice — see docs/memory-architecture.md.

    docker compose exec backend python -m scripts.purge_dataset --ticker AAPL --yes
    docker compose exec backend python -m scripts.purge_dataset --ticker AAPL --older-than-days 7 --yes
    # or: make purge t=AAPL   |   make purge t=AAPL keep=7
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from scripts.backfill_ticker import backfill
from src.database.session import get_sessionmaker
from src.repositories.company_repo import CompanyRepository
from src.repositories.ingestion_repo import IngestionRepository
from src.services.memory_service import get_memory_service


async def purge(ticker: str, *, older_than_days: int | None) -> None:
    """Forget ``company_{ticker}`` and clear its ledger; optionally rebuild.

    Args:
        ticker: Ticker symbol; dataset is ``company_{ticker}``.
        older_than_days: If set, after forgetting, re-backfill the last N days so only
            recent (non-stale) items are restored. If None, the dataset stays empty.
    """
    ticker = ticker.upper()
    sessionmaker = get_sessionmaker()

    # 1. Forget the whole Cognee dataset (idempotent) + clear the dedup ledger so a
    #    subsequent re-backfill is not skipped by the dedup check.
    async with sessionmaker() as session:
        company = await CompanyRepository(session).get_by_ticker(ticker)
        await get_memory_service().delete(ticker)
        removed = 0
        if company is not None:
            removed = await IngestionRepository(session).delete_for_company(company.id)
        await session.commit()
    print(f"  forgot cognee dataset company_{ticker}; cleared {removed} ledger row(s)")

    # 2. Staleness mode: rebuild from the retained window (its own session + commit).
    if older_than_days is not None:
        print(f"  rebuilding from the last {older_than_days}d...")
        added = await backfill(ticker, days=older_than_days, news=True, price=True)
        print(f"  rebuilt: {added} item(s) re-ingested into company_{ticker}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forget a Cognee dataset for a ticker (admin).")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL.")
    parser.add_argument(
        "--older-than-days",
        dest="older_than_days",
        type=int,
        default=None,
        metavar="N",
        help="Keep only the last N days: forget, then re-backfill that window. "
        "Omit for a full purge (leaves the dataset empty).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm the destructive purge (required to actually run).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ticker = args.ticker.upper()

    if args.older_than_days is not None and args.older_than_days < 0:
        print("error: --older-than-days must be >= 0", file=sys.stderr)
        return 2
    if not args.yes:
        print(f"refusing to purge company_{ticker} without --yes", file=sys.stderr)
        return 2

    mode = "full purge" if args.older_than_days is None else f"keep last {args.older_than_days}d"
    print(f"Purging company_{ticker} ({mode})...")
    asyncio.run(purge(ticker, older_than_days=args.older_than_days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
