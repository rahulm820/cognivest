#!/usr/bin/env python3
"""Backfill a ticker: fetch prices + news → Cognee (add + cognify). Celery-free.

Runs the collectors synchronously (no queue) so the demo path has no Celery
dependency. Idempotent: content-hash dedup runs before ``cognee.add()``, so
re-running a backfill only ingests genuinely new items.

    docker compose exec backend python -m scripts.backfill_ticker --ticker AAPL
    # or: make backfill t=AAPL
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from src.collectors.news_collector import NewsCollector
from src.collectors.price_collector import PriceCollector
from src.database.session import get_sessionmaker
from src.repositories.company_repo import CompanyRepository
from src.repositories.ingestion_repo import IngestionRepository
from src.services.collector_service import CollectorService
from src.services.memory_service import get_memory_service


async def backfill(ticker: str, *, days: int, news: bool, price: bool) -> int:
    """Fetch + ingest prices and/or news for ``ticker``. Returns new-item count."""
    ticker = ticker.upper()
    sessionmaker = get_sessionmaker()
    total = 0
    async with sessionmaker() as session:
        company = await CompanyRepository(session).get_or_create(ticker)
        service = CollectorService(get_memory_service(), IngestionRepository(session))

        if price:
            count = await service.run_for_ticker(
                ticker, PriceCollector(days=days), company_id=company.id
            )
            print(f"  price: {count} new item(s)")
            total += count

        if news:
            count = await service.run_for_ticker(
                ticker,
                NewsCollector(company_name=company.name, days=days),
                company_id=company.id,
            )
            print(f"  news:  {count} new item(s)")
            total += count

        await session.commit()
    print(f"Done: {total} new item(s) ingested into company_{ticker}.")
    return total


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
    print(f"Backfilling {ticker} ({args.days}d)...")
    asyncio.run(
        backfill(
            ticker,
            days=args.days,
            news=not args.no_news,
            price=not args.no_price,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
