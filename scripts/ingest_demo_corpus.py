#!/usr/bin/env python3
"""Ingest the hand-curated demo news corpus into Cognee (issue #17).

GDELT's live news fetch is 429-blocked for the demo, so the demo's news citations
come from a small, source-verified corpus (``data/demo_corpus.json``) instead of the
:class:`~src.collectors.news_collector.NewsCollector`. This loader feeds each corpus
item through the EXISTING ingestion path — ``memory_service.ingest`` with the same
citation-metadata contract ``CollectorService._metadata`` builds — so nothing about
provenance, dataset scoping, or the single Cognee seam is re-implemented here. Only
the vendor-fetch step is swapped for reading a JSON file.

Pipeline (mirrors :class:`~src.services.collector_service.CollectorService`):
    read JSON -> per item: render + metadata -> memory_service.ingest(cognify=False)
    -> ONE cognify per ticker (``reflect``) at the end. ``cognify`` is the expensive
    step and must never run per item.

Run (Docker):
    docker compose exec backend python -m scripts.ingest_demo_corpus --dry-run
    docker compose exec backend python -m scripts.ingest_demo_corpus              # real
    docker compose exec backend python -m scripts.ingest_demo_corpus --ticker AAPL

NOTE (compose mount gap): the backend service mounts ``./backend`` and ``./scripts``
but NOT ``./data``. For an in-container REAL run either add a ``./data:/app/data``
mount, or pass ``--corpus /path/to/demo_corpus.json`` pointing at a mounted location.
``--dry-run`` on the host resolves the repo-root ``data/`` directory directly.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Pure dataclass, no heavy deps — safe to import even in a bare host env so --dry-run
# runs without the full backend stack. The MemoryService import is deferred into the
# real-ingest path (see :func:`_ingest`) so a dry run needs no DB/LLM wiring.
from src.collectors.base import NormalizedItem

# Diagnostic-only mirror of the seam's provenance markers + snippet cap
# (``src.memory.cognee_client._PROVENANCE_OPEN`` / ``_PROVENANCE_CLOSE`` and the
# ~160-char Evidence-snippet cap noted in ``_parse_provenance``). Used ONLY to preview
# header length in --dry-run; the REAL provenance header is built by the seam
# (``cognee_client._with_provenance``) at ingest time — this script never
# re-implements it. Keep these in sync with that module.
_PROVENANCE_OPEN = "[PROVENANCE]"
_PROVENANCE_CLOSE = "[/PROVENANCE]"
_SNIPPET_CAP = 160
# Field emission order the seam uses; source_url + published_at go FIRST so they
# survive truncation, title is the sacrificial tail (see cognee_client docstrings).
_PROVENANCE_FIELD_ORDER = ("source_url", "published_at", "source", "title")


def _parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp string into a tz-aware UTC datetime."""
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _to_item(record: dict[str, str]) -> NormalizedItem:
    """Map one corpus JSON record onto a :class:`NormalizedItem` (the collector shape)."""
    return NormalizedItem(
        ticker=str(record["ticker"]).upper(),
        title=str(record["title"]),
        body=str(record["summary"]),
        source=str(record["source"]),
        ts=_parse_ts(str(record["published_at"])),
        source_url=str(record["source_url"]) if record.get("source_url") else None,
    )


def _render(item: NormalizedItem) -> str:
    """Text ingested into Cognee — mirrors ``CollectorService._render`` (issue #17)."""
    if item.title and item.title not in item.body:
        return f"{item.title}\n\n{item.body}"
    return item.body


def _metadata(item: NormalizedItem) -> dict[str, str]:
    """Citation metadata dict — mirrors ``CollectorService._metadata`` (issue #17).

    Same keys the real collector emits, so the seam's provenance header is identical to
    a live-collected item. This is NOT a re-implementation of provenance: the header
    itself is still assembled by ``cognee_client._with_provenance`` at ingest time.
    """
    meta: dict[str, str] = {"title": item.title, "source": item.source}
    if item.source_url:
        meta["source_url"] = item.source_url
    meta["published_at"] = item.ts.isoformat()
    return meta


def _provenance_preview(meta: dict[str, str]) -> str:
    """Reconstruct the seam's provenance header for a LENGTH PREVIEW only (dry-run)."""
    fields = [f"{key}={meta[key]}" for key in _PROVENANCE_FIELD_ORDER if meta.get(key)]
    return f"{_PROVENANCE_OPEN} " + " | ".join(fields) + f" {_PROVENANCE_CLOSE}"


def _candidate_paths(explicit: str | None) -> list[Path]:
    """Ordered corpus-file lookup: explicit --corpus, then repo-root/container defaults."""
    if explicit:
        return [Path(explicit)]
    repo_root = Path(__file__).resolve().parents[1]
    return [
        Path.cwd() / "data" / "demo_corpus.json",
        repo_root / "data" / "demo_corpus.json",
        Path("/app/data/demo_corpus.json"),
    ]


def _load_corpus(explicit: str | None) -> tuple[Path, list[dict[str, str]]]:
    """Locate and parse the corpus JSON, returning (path, item records)."""
    tried = _candidate_paths(explicit)
    for path in tried:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            records = data.get("items", []) if isinstance(data, dict) else data
            return path, list(records)
    joined = "\n  ".join(str(path) for path in tried)
    raise FileNotFoundError(
        "demo corpus not found. Tried:\n  "
        + joined
        + "\nPass --corpus PATH, or mount ./data into the backend container "
        "(compose mounts ./backend and ./scripts, not ./data)."
    )


def _group_by_ticker(
    records: list[dict[str, str]], ticker_filter: str | None
) -> dict[str, list[dict[str, str]]]:
    """Group records by ticker (insertion order preserved), applying --ticker filter."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        ticker = str(record["ticker"]).upper()
        if ticker_filter and ticker != ticker_filter:
            continue
        grouped[ticker].append(record)
    return grouped


def _dry_run(grouped: dict[str, list[dict[str, str]]]) -> None:
    """Print exactly what would be ingested — including provenance-header length."""
    total = 0
    for ticker, records in grouped.items():
        print(f"\n=== company_{ticker}: {len(records)} item(s), then cognify x1 ===")
        for record in records:
            item = _to_item(record)
            content = _render(item)
            meta = _metadata(item)
            header = _provenance_preview(meta)
            length = len(header)
            note = "fits" if length <= _SNIPPET_CAP else f"TRUNCATES ({length}>{_SNIPPET_CAP})"
            print(f"\n  - {item.title!r}")
            print(f"      published_at : {meta['published_at']}")
            print(f"      source       : {meta['source']}")
            print(f"      source_url   : {item.source_url}")
            print(f"      metadata     : {meta}")
            print(f"      content[:80] : {content[:80]!r}")
            print(f"      prov header  : {length} chars in snippet cap {_SNIPPET_CAP} -> {note}")
            total += 1
    print(
        f"\n[dry-run] {total} item(s) across {len(grouped)} ticker(s); nothing ingested. "
        "source_url + published_at are emitted first, so they survive any truncation; "
        "an over-cap title is the sacrificial tail."
    )


async def _ingest(grouped: dict[str, list[dict[str, str]]]) -> int:
    """Ingest each item via the real seam, one cognify per ticker at the end."""
    # Deferred import: pulls the full backend stack (DB/LLM wiring). Kept out of module
    # scope so --dry-run stays runnable in a bare env.
    from src.services.memory_service import get_memory_service

    service = get_memory_service()
    total = 0
    for ticker, records in grouped.items():
        for record in records:
            item = _to_item(record)
            await service.ingest(
                ticker, _render(item), metadata=_metadata(item), cognify=False
            )
            total += 1
            print(f"[add] company_{ticker} <- {item.title!r}")
        # ONE cognify for the whole ticker batch — the expensive step, never per item.
        await service.reflect(ticker)
        print(f"[cognify] company_{ticker} graph built")
    return total


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest the demo news corpus (issue #17) into Cognee."
    )
    parser.add_argument("--ticker", help="Only ingest this ticker (e.g. AAPL).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be ingested (incl. provenance-header length); ingest nothing.",
    )
    parser.add_argument(
        "--corpus", help="Path to demo_corpus.json (overrides the default lookup)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: load the corpus, then dry-run or ingest."""
    args = parse_args(argv)
    ticker_filter = args.ticker.upper() if args.ticker else None
    path, records = _load_corpus(args.corpus)
    grouped = _group_by_ticker(records, ticker_filter)
    if not grouped:
        print(f"No corpus items match ticker={ticker_filter!r} in {path}.")
        return 1

    loaded = sum(len(items) for items in grouped.values())
    print(f"Loaded {loaded} item(s) from {path}")
    if args.dry_run:
        _dry_run(grouped)
        return 0

    total = asyncio.run(_ingest(grouped))
    print(f"\nDone: ingested {total} item(s); one cognify per ticker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
