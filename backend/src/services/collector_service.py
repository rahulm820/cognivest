"""Collector orchestration service.

Implements the per-ticker ingestion pipeline:
``fetch → normalize → dedup → memory_service.ingest``. Celery-free — callable from
a script or route. Each run is idempotent because the content-hash dedup check runs
before ``cognee.add()``; ``cognify`` runs once per batch, not per item.
"""

from __future__ import annotations

import uuid

from src.collectors.base import Collector, NormalizedItem
from src.collectors.dedup import content_hash
from src.config.logging import get_logger
from src.repositories.ingestion_repo import IngestionRepository
from src.services.memory_service import MemoryService

logger = get_logger(__name__)


class CollectorService:
    """Orchestrates a single collector run for a ticker."""

    def __init__(
        self,
        memory_service: MemoryService,
        ingestion_repo: IngestionRepository,
    ) -> None:
        """Bind to the memory service and ingestion (dedup) repository."""
        self._memory_service = memory_service
        self._ingestion_repo = ingestion_repo

    async def run_for_ticker(
        self,
        ticker: str,
        collector: Collector,
        *,
        company_id: uuid.UUID,
    ) -> int:
        """Run one collection pass for a ticker through a given collector.

        Pipeline: fetch (collector) → dedup (skip content already ingested for this
        company) → ``memory_service.ingest`` (add only) → mark ingested → a single
        ``cognify`` for the whole batch. Returns the count of NEW items ingested.

        Args:
            ticker: The company ticker; memory is scoped to ``company_{ticker}``.
            collector: The vendor collector to run (price, news, ...).
            company_id: The company's PK, for the per-company dedup ledger.
        """
        ticker = ticker.upper()
        items = await collector.collect(ticker)
        new_count = 0
        for item in items:
            digest = content_hash(item)
            if await self._ingestion_repo.exists_hash(company_id, digest):
                continue
            await self._memory_service.ingest(
                ticker,
                self._render(item),
                metadata=self._metadata(item),
                cognify=False,
            )
            await self._ingestion_repo.mark_ingested(
                company_id, digest, source_url=item.source_url
            )
            new_count += 1

        if new_count:
            # Build the graph once for the whole batch (cognify is the expensive step).
            await self._memory_service.reflect(ticker)
        logger.info(
            "collector.run",
            ticker=ticker,
            collector=collector.name,
            fetched=len(items),
            ingested=new_count,
        )
        return new_count

    @staticmethod
    def _render(item: NormalizedItem) -> str:
        """Render a normalized item to the text ingested into Cognee."""
        if item.title and item.title not in item.body:
            return f"{item.title}\n\n{item.body}"
        return item.body

    @staticmethod
    def _metadata(item: NormalizedItem) -> dict[str, str]:
        """Citation metadata carried into Cognee as a provenance header."""
        meta: dict[str, str] = {"title": item.title, "source": item.source}
        if item.source_url:
            meta["source_url"] = item.source_url
        meta["published_at"] = item.ts.isoformat()
        return meta
