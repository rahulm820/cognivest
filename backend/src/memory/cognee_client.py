"""THE single Cognee integration seam.

================================================================================
SINGLE-SEAM RULE
--------------------------------------------------------------------------------
This module is the *only* file in the entire backend permitted to import the
Cognee SDK. Do NOT import ``cognee`` anywhere else. All memory operations funnel
through ``services/memory_service.py``, which in turn calls this thin async
wrapper. Keeping Cognee behind one seam means:

  * the rest of the codebase has no Cognee dependency and is trivially mockable;
  * Cognee configuration (vector/graph backends) can change without touching callers;
  * we never accidentally reimplement retrieval/embedding/reranking — Cognee owns it.

This wrapper deliberately contains NO business logic. It maps our typed calls onto
Cognee's ``add`` / ``cognify`` / ``search`` / ``recall`` / ``delete`` primitives and
scopes everything to a single dataset (``company_{ticker}``) via
``memory/dataset_naming.py``.
================================================================================

Phase 0 scaffold: real Cognee calls are stubbed. Bodies raise
``NotImplementedError`` with ``# TODO(phase-3)`` markers.
"""

from __future__ import annotations

from typing import Any

# NOTE: This is the ONLY permitted Cognee import in the codebase.
# It is wrapped so the scaffold imports cleanly even if the SDK is absent.
try:  # pragma: no cover - import guard for scaffold environments
    import cognee  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    cognee = None  # type: ignore[assignment]

from src.config.logging import get_logger
from src.memory.dataset_naming import dataset_name

logger = get_logger(__name__)


class CogneeClient:
    """Thin async wrapper around the Cognee SDK, scoped per-ticker dataset.

    Each method targets the dataset ``company_{ticker}``. Methods are coroutines
    because every Cognee operation is I/O- and/or compute-bound.
    """

    async def add(self, ticker: str, content: str, *, metadata: dict[str, Any] | None = None) -> None:
        """Add normalized content to the ticker's dataset (``cognee.add``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            content: Normalized text to ingest.
            metadata: Citation metadata (source_url, published_at, job id, ...).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        dataset = dataset_name(ticker)
        logger.debug("cognee.add", dataset=dataset, has_metadata=metadata is not None)
        # TODO(phase-3): await cognee.add(content, dataset_name=dataset, ...metadata)
        raise NotImplementedError("TODO(phase-3): wire cognee.add() for dataset %s" % dataset)

    async def cognify(self, ticker: str) -> None:
        """Build/update the per-company knowledge graph (``cognee.cognify``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        dataset = dataset_name(ticker)
        logger.debug("cognee.cognify", dataset=dataset)
        # TODO(phase-3): await cognee.cognify(datasets=[dataset])
        raise NotImplementedError("TODO(phase-3): wire cognee.cognify() for dataset %s" % dataset)

    async def search(
        self,
        ticker: str,
        query: str,
        *,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve ranked hits from the ticker's dataset (``cognee.search``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            query: The natural-language query.
            top_k: Maximum number of hits.
            filters: Optional filters (e.g. date range) passed to Cognee.

        Returns:
            A list of ranked result dicts (text + score + source metadata).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        dataset = dataset_name(ticker)
        logger.debug("cognee.search", dataset=dataset, top_k=top_k)
        # TODO(phase-3): return await cognee.search(query, dataset_name=dataset, ...)
        raise NotImplementedError("TODO(phase-3): wire cognee.search() for dataset %s" % dataset)

    async def recall(
        self, ticker: str, query: str, *, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Graph-aware recall over the ticker's dataset (``cognee.recall``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            query: The natural-language query.
            filters: Optional filters passed to Cognee.

        Returns:
            A list of recalled nodes/passages with metadata.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        dataset = dataset_name(ticker)
        logger.debug("cognee.recall", dataset=dataset)
        # TODO(phase-3): return await cognee.recall(query, dataset_name=dataset, ...)
        raise NotImplementedError("TODO(phase-3): wire cognee.recall() for dataset %s" % dataset)

    async def delete(self, ticker: str, *, filters: dict[str, Any] | None = None) -> None:
        """Delete a dataset or a filtered slice of it (``cognee.delete``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            filters: Optional filters (e.g. date range) to delete a slice only.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        dataset = dataset_name(ticker)
        logger.debug("cognee.delete", dataset=dataset, sliced=filters is not None)
        # TODO(phase-3): await cognee.delete(dataset_name=dataset, ...filters)
        raise NotImplementedError("TODO(phase-3): wire cognee.delete() for dataset %s" % dataset)


_client: CogneeClient | None = None


def get_cognee_client() -> CogneeClient:
    """Return the process-wide :class:`CogneeClient` singleton."""
    global _client
    if _client is None:
        _client = CogneeClient()
    return _client
