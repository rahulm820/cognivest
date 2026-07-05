"""Unit tests for the forget/delete path (issue #9).

Covers the two ``src``-side pieces the forget lifecycle rests on:

* ``MemoryService.delete`` always forgets the WHOLE dataset via the seam and never
  passes a date slice (Cognee 1.2.2 has no sliced delete); ``date_range`` is advisory.
* ``IngestionRepository.delete_for_company`` clears the dedup ledger and reports how
  many rows went, so a re-backfill can repopulate without being deduped away.

Both use lightweight mocks — no live Cognee, no real database.
"""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from src.repositories.ingestion_repo import IngestionRepository
from src.schemas.common import DateRange
from src.services.memory_service import MemoryService


async def test_delete_forgets_whole_dataset() -> None:
    """delete(ticker) delegates to the seam's whole-dataset forget, once."""
    client = AsyncMock()
    service = MemoryService(client=client)

    await service.delete("aapl")

    client.delete.assert_awaited_once_with("aapl")


async def test_delete_ignores_date_range() -> None:
    """A date_range is advisory: still a whole-dataset forget, no filters to the seam."""
    client = AsyncMock()
    service = MemoryService(client=client)
    date_range = DateRange(**{"from": date(2026, 1, 1), "to": date(2026, 2, 1)})

    await service.delete("AAPL", date_range=date_range)

    client.delete.assert_awaited_once_with("AAPL")
    # The seam is never asked to slice — the only positional arg is the ticker.
    assert client.delete.await_args.kwargs == {}


async def test_delete_for_company_returns_rowcount() -> None:
    """delete_for_company returns the number of ledger rows removed."""
    session = AsyncMock()
    result = MagicMock()
    result.rowcount = 3
    session.execute.return_value = result
    repo = IngestionRepository(session)

    removed = await repo.delete_for_company(uuid.uuid4())

    assert removed == 3
    session.execute.assert_awaited_once()


async def test_delete_for_company_handles_none_rowcount() -> None:
    """A driver that reports rowcount=None is coerced to 0, not a crash."""
    session = AsyncMock()
    result = MagicMock()
    result.rowcount = None
    session.execute.return_value = result
    repo = IngestionRepository(session)

    assert await repo.delete_for_company(uuid.uuid4()) == 0
