"""Ingestion + dedup data access.

Owns the dedup ledger (``ingested_items``) and ingestion job state. The dedup hash
check here is what guarantees we never re-ingest duplicate content into Cognee.
"""

from __future__ import annotations

import uuid

from src.models.ingested_item import IngestedItem
from src.repositories.base import BaseRepository


class IngestionRepository(BaseRepository[IngestedItem]):
    """Postgres data access for the dedup ledger + ingestion jobs."""

    model = IngestedItem

    async def exists_hash(self, company_id: uuid.UUID, content_hash: str) -> bool:
        """Return True if ``content_hash`` was already ingested for the company.

        This is the dedup check performed BEFORE ``cognee.add()``.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-2): select 1 from ingested_items where company_id & content_hash
        raise NotImplementedError("TODO(phase-2): implement IngestionRepository.exists_hash")

    async def mark_ingested(
        self,
        company_id: uuid.UUID,
        content_hash: str,
        *,
        source_url: str | None = None,
    ) -> IngestedItem:
        """Record that content was ingested (insert into the dedup ledger).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-2): insert IngestedItem(company_id, content_hash, source_url)
        raise NotImplementedError("TODO(phase-2): implement IngestionRepository.mark_ingested")
