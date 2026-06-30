"""Memory orchestration service — the ONLY caller of the Cognee client.

Every memory operation in the backend funnels through here. It wraps
``memory/cognee_client.py`` (the single Cognee seam) and exposes a clean, typed,
mockable surface to the rest of the app: ``ingest``, ``search``, ``assemble_context``,
``reflect``, ``delete``. No other module may touch the Cognee client.

This service contains orchestration only — it does NOT reimplement retrieval,
embedding, reranking, or summarization (Cognee owns all of that).
"""

from __future__ import annotations

from typing import Any

from src.memory.cognee_client import CogneeClient, get_cognee_client
from src.schemas.common import DateRange
from src.schemas.memory import MemoryContextOut, MemorySearchOut


class MemoryService:
    """Typed orchestration over the Cognee seam, scoped per ticker."""

    def __init__(self, client: CogneeClient | None = None) -> None:
        """Bind to a Cognee client (defaults to the shared singleton)."""
        self._client = client or get_cognee_client()

    async def ingest(
        self,
        ticker: str,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add content to a ticker's dataset, then trigger graph build.

        Orchestrates ``cognee.add`` followed by (decoupled) ``cognee.cognify``.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-3): await self._client.add(...); enqueue/await cognify
        raise NotImplementedError("TODO(phase-3): implement MemoryService.ingest")

    async def search(
        self,
        ticker: str,
        query: str,
        *,
        date_range: DateRange | None = None,
        top_k: int = 10,
    ) -> MemorySearchOut:
        """Retrieve ranked hits for a query scoped to a ticker's dataset.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-3): results = await self._client.search(...); map -> MemorySearchOut
        raise NotImplementedError("TODO(phase-3): implement MemoryService.search")

    async def assemble_context(
        self,
        ticker: str,
        query: str,
        *,
        date_range: DateRange | None = None,
    ) -> MemoryContextOut:
        """Assemble a pre-LLM context block (chunks + graph snippet) for a query.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-3): recall + format into a context block + citations
        raise NotImplementedError("TODO(phase-3): implement MemoryService.assemble_context")

    async def reflect(self, ticker: str) -> None:
        """Trigger a consolidation/cognify reflection pass for a ticker.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-3): await self._client.cognify(ticker)  # consolidation pass
        raise NotImplementedError("TODO(phase-3): implement MemoryService.reflect")

    async def delete(self, ticker: str, *, date_range: DateRange | None = None) -> None:
        """Purge a ticker's dataset or a date-bounded slice of it.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-3): await self._client.delete(ticker, filters=date_range)
        raise NotImplementedError("TODO(phase-3): implement MemoryService.delete")
