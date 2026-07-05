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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.memory.dataset_naming import dataset_name, normalize_ticker
from src.middleware.auth_middleware import require_service_token
from src.repositories.company_repo import CompanyRepository
from src.repositories.ingestion_repo import IngestionRepository
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
from src.services.memory_service import get_memory_service

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
async def delete(payload: MemoryDelete, db: AsyncSession = Depends(get_db)) -> MemoryAck:
    """Forget a company's entire Cognee dataset and clear its dedup ledger.

    Cognee 1.2.2 has no per-item/date-sliced deletion (spike CONTRADICTION #2), so a
    ``date_range`` on the payload is advisory only — the WHOLE ``company_{ticker}``
    dataset is forgotten regardless. Date-bounded "staleness" purges (keep only the
    last N days) are driven by ``scripts/purge_dataset.py``, which forgets the dataset
    then re-backfills the retained window (issue #9). Clearing the ledger here lets a
    subsequent re-backfill repopulate without being skipped by the dedup check.

    Idempotent: forgetting a never-created dataset (and clearing an absent company's
    ledger) is a no-op success.

    Raises:
        HTTPException: 400 if the ticker fails format validation.
    """
    try:
        normalized = normalize_ticker(payload.ticker)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await get_memory_service().delete(normalized, date_range=payload.date_range)

    removed = 0
    company = await CompanyRepository(db).get_by_ticker(normalized)
    if company is not None:
        removed = await IngestionRepository(db).delete_for_company(company.id)

    return MemoryAck(
        dataset_name=dataset_name(normalized),
        detail=f"forgot dataset; cleared {removed} dedup-ledger row(s)",
    )
