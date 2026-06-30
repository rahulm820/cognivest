"""Internal memory routes (the Cognee-backed wrapper surface, ARCHITECTURE.md §5.7).

These endpoints are INTERNAL-ONLY: every route is guarded by the service-to-service
token (and network isolation in deployment). They delegate to ``MemoryService`` — the
only caller of the Cognee client. Handlers stay thin.

    POST   /memory/store      → ingest (add + cognify)
    POST   /memory/search     → retrieval
    POST   /memory/context    → pre-LLM context assembly
    POST   /memory/reflection → consolidation/cognify pass
    DELETE /memory/delete     → purge dataset or slice
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.middleware.auth_middleware import require_service_token
from src.schemas.memory import (
    MemoryAck,
    MemoryContext,
    MemoryContextOut,
    MemoryDelete,
    MemoryReflection,
    MemorySearch,
    MemorySearchOut,
    MemoryStore,
)

router = APIRouter(
    prefix="/memory",
    tags=["memory (internal)"],
    dependencies=[Depends(require_service_token)],
)


@router.post("/store", response_model=MemoryAck, status_code=status.HTTP_202_ACCEPTED)
async def store(payload: MemoryStore) -> MemoryAck:
    """Ingest normalized content into a company's dataset (add + cognify).

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): memory_service.ingest(payload.ticker, payload.content, metadata=...)
    raise NotImplementedError("TODO(phase-3): implement memory.store")


@router.post("/search", response_model=MemorySearchOut)
async def search(payload: MemorySearch) -> MemorySearchOut:
    """Retrieve ranked hits from a company's dataset.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): memory_service.search(payload.ticker, payload.query, ...)
    raise NotImplementedError("TODO(phase-3): implement memory.search")


@router.post("/context", response_model=MemoryContextOut)
async def context(payload: MemoryContext) -> MemoryContextOut:
    """Assemble a pre-LLM context block for a query.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): memory_service.assemble_context(payload.ticker, payload.query, ...)
    raise NotImplementedError("TODO(phase-3): implement memory.context")


@router.post("/reflection", response_model=MemoryAck, status_code=status.HTTP_202_ACCEPTED)
async def reflection(payload: MemoryReflection) -> MemoryAck:
    """Trigger a consolidation/cognify reflection pass for a company.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): memory_service.reflect(payload.ticker)
    raise NotImplementedError("TODO(phase-3): implement memory.reflection")


@router.delete("/delete", response_model=MemoryAck)
async def delete(payload: MemoryDelete) -> MemoryAck:
    """Purge a company's dataset or a date-bounded slice of it.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): memory_service.delete(payload.ticker, date_range=payload.date_range)
    raise NotImplementedError("TODO(phase-3): implement memory.delete")
