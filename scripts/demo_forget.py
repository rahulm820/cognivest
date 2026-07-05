#!/usr/bin/env python3
"""Prove the forget lifecycle end to end (issue #9 acceptance).

Runs the demonstrable sequence the "Best Use of Cognee" judges look for:

    1. backfill   — ingest prices + news for a ticker (build the graph)
    2. query      — ask a question; the answer CITES an ingested article
    3. forget     — purge the whole company_{ticker} dataset + clear the ledger
    4. query      — same question; the answer NO LONGER cites that article

The point is step 2 vs step 4: memory demonstrably changed. Real mechanism =
whole-dataset ``cognee.forget()`` (Cognee 1.2.2 has no per-item delete), so after
the forget the query falls back to the honest "no data ingested yet" answer with an
empty citation list.

    docker compose exec backend python -m scripts.demo_forget --ticker AAPL

Note: this exercises the live Cognee + LLM path (cognify + GRAPH_COMPLETION), so it
needs a working LLM key with available quota. It is a demo/acceptance script, not a
unit test.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from scripts.backfill_ticker import backfill
from scripts.purge_dataset import purge
from src.schemas.memory import MemoryAnswerOut
from src.services.memory_service import get_memory_service

_DEFAULT_QUESTION = "What recent news is there about this company?"


def _print_answer(label: str, result: MemoryAnswerOut) -> None:
    """Print an answer + its citation URLs under a labelled header."""
    print(f"\n=== {label} ===")
    print(f"answer:    {result.answer[:400]}")
    if result.citations:
        print(f"citations ({len(result.citations)}):")
        for cite in result.citations:
            print(f"  - {cite.title}  {cite.url or ''}".rstrip())
    else:
        print("citations: (none)")


async def demo(ticker: str, question: str, *, days: int) -> int:
    """Run backfill → query → forget → query and print the before/after citations."""
    ticker = ticker.upper()
    memory = get_memory_service()

    print(f"[1/4] Backfilling {ticker} ({days}d)...")
    ingested = await backfill(ticker, days=days, news=True, price=True)
    print(f"      ingested {ingested} item(s)")

    print(f"[2/4] Querying {ticker} (expect a cited answer)...")
    before = await memory.answer(ticker, question)
    _print_answer("BEFORE forget", before)

    print(f"\n[3/4] Forgetting {ticker} (whole-dataset purge + ledger clear)...")
    await purge(ticker, older_than_days=None)

    print(f"[4/4] Querying {ticker} again (expect NO citations)...")
    after = await memory.answer(ticker, question)
    _print_answer("AFTER forget", after)

    changed = bool(before.citations) and not after.citations
    print("\n----------------------------------------")
    if changed:
        print("PASS: memory changed — the article is cited before forget and gone after.")
        return 0
    print(
        "INCONCLUSIVE: expected citations before and none after. "
        "Check that the backfill ingested news and that the LLM quota was available."
    )
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo the forget lifecycle for a ticker.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL.")
    parser.add_argument(
        "--question",
        default=_DEFAULT_QUESTION,
        help="Question to ask before and after forgetting (default: %(default)r).",
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Backfill window in days (default: %(default)s)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(demo(args.ticker, args.question, days=args.days))


if __name__ == "__main__":
    sys.exit(main())
