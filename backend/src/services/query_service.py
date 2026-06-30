"""Query service: orchestrates retrieval + answer formatting.

Coordinates ``memory_service.search`` (Cognee retrieval = the RAG step) with
``ai.answer_formatter`` (the single Claude call) to produce a cited answer, and logs
the query for audit. Holds no Cognee imports and no SQL.
"""

from __future__ import annotations

import uuid

from src.services.memory_service import MemoryService
from src.schemas.query import QueryRequest, QueryResponse


class QueryService:
    """Business logic for the natural-language query path."""

    def __init__(self, memory_service: MemoryService) -> None:
        """Bind to the memory service (the only Cognee caller)."""
        self._memory_service = memory_service

    async def answer(
        self,
        *,
        user_id: uuid.UUID,
        ticker: str,
        request: QueryRequest,
    ) -> QueryResponse:
        """Retrieve scoped context and format a cited answer.

        Pipeline: ``memory_service.search`` → ``answer_formatter.format_answer`` →
        audit log. Optionally cache identical recent queries (ARCHITECTURE.md §2.5).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-4):
        #   results = await memory_service.search(ticker, request.question,
        #                                         date_range=request.date_range)
        #   response = await format_answer(ticker=ticker, question=..., results=...)
        #   await query_log_repo.record(user_id, ticker, request.question)
        raise NotImplementedError("TODO(phase-4): implement QueryService.answer")
