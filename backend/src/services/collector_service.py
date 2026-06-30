"""Collector orchestration service.

Implements the per-ticker ingestion pipeline:
``fetch → normalize → dedup → memory_service.ingest``. Called by Celery tasks. Each
run is idempotent because dedup happens before ``cognee.add()``.
"""

from __future__ import annotations

from src.collectors.base import Collector
from src.repositories.ingestion_repo import IngestionRepository
from src.services.memory_service import MemoryService


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

    async def run_for_ticker(self, ticker: str, collector: Collector) -> int:
        """Run one collection pass for a ticker through a given collector.

        Pipeline: fetch (collector) → normalize → dedup (skip seen) →
        ``memory_service.ingest`` → mark ingested. Returns the count of NEW items.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-2):
        #   items = await collector.collect(ticker)
        #   for item in items:
        #       if await is_duplicate(item, company_id, ingestion_repo): continue
        #       await memory_service.ingest(ticker, item.body, metadata=...)
        #       await ingestion_repo.mark_ingested(company_id, content_hash(item), ...)
        raise NotImplementedError("TODO(phase-2): implement CollectorService.run_for_ticker")
