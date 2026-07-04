"""Ingestion + dedup data access.

Owns the dedup ledger (``ingested_items``) and ingestion job state. The dedup hash
check here is what guarantees we never re-ingest duplicate content into Cognee.
"""

from __future__ import annotations

import uuid

from sqlalchemy import exists, select

from src.models.ingested_item import IngestedItem
from src.repositories.base import BaseRepository


class IngestionRepository(BaseRepository[IngestedItem]):
    """Postgres data access for the dedup ledger + ingestion jobs."""

    model = IngestedItem

    async def exists_hash(self, company_id: uuid.UUID, content_hash: str) -> bool:
        """Return True if ``content_hash`` was already ingested for the company.

        This is the dedup check performed BEFORE ``cognee.add()``.
        """
        result = await self.session.execute(
            select(
                exists().where(
                    IngestedItem.company_id == company_id,
                    IngestedItem.content_hash == content_hash,
                )
            )
        )
        return bool(result.scalar())

    async def mark_ingested(
        self,
        company_id: uuid.UUID,
        content_hash: str,
        *,
        source_url: str | None = None,
    ) -> IngestedItem:
        """Record that content was ingested (insert into the dedup ledger)."""
        return await self.add(
            IngestedItem(
                company_id=company_id,
                content_hash=content_hash,
                source_url=source_url,
            )
        )
