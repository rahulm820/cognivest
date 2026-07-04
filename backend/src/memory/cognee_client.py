"""THE single Cognee integration seam.

================================================================================
SINGLE-SEAM RULE
--------------------------------------------------------------------------------
This module is the *only* file in the entire backend permitted to import the
Cognee SDK. Do NOT import ``cognee`` anywhere else. All memory operations funnel
through ``services/memory_service.py``, which in turn calls this thin async
wrapper. Keeping Cognee behind one seam means:

  * the rest of the codebase has no Cognee dependency and is trivially mockable;
  * Cognee configuration (vector/graph/LLM backends) can change without touching callers;
  * we never accidentally reimplement retrieval/embedding/reranking — Cognee owns it.

This wrapper deliberately contains NO business logic and NO configuration. Cognee's
LLM (Gemini) + embeddings (fastembed) are configured via the repo-root ``.env``
(``LLM_*`` / ``EMBEDDING_*``), which Cognee reads at import — see issue #3 and
``docs/spike-cognee-1.2.2.md`` §3. This module just maps our typed calls onto
Cognee's primitives, scoped to a single dataset (``company_{ticker}``).

Implemented against **cognee 1.2.2** (pinned). API shape per the spike:
  * ``add`` targets a dataset via ``dataset_name=`` (singular);
  * ``cognify`` / ``search`` / ``recall`` target via ``datasets=[...]`` (plural) —
    ``search`` has NO ``dataset_name`` and NO ``filters`` param (spike CONTRADICTION #1);
  * deletion uses ``forget(dataset=...)`` — top-level ``delete()`` is deprecated
    (spike CONTRADICTION #2).
================================================================================
"""

from __future__ import annotations

from typing import Any

# NOTE: This is the ONLY permitted Cognee import in the codebase.
# It is wrapped so the scaffold imports cleanly even if the SDK is absent.
try:  # pragma: no cover - import guard for scaffold environments
    import cognee  # type: ignore[import-untyped]
    from cognee.modules.search.types import SearchType  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    cognee = None  # type: ignore[assignment]
    SearchType = None  # type: ignore[assignment]

from src.config.logging import get_logger
from src.memory.dataset_naming import dataset_name

logger = get_logger(__name__)

# Retrieval mode. GRAPH_COMPLETION is Cognee's default and the spike-verified path
# (docs/spike-cognee-1.2.2.md §4): vector + graph retrieval yielding a grounded,
# generated answer in ``result["search_result"]``. Kept internal so callers never
# depend on Cognee's ``SearchType``.
_SEARCH_TYPE = SearchType.GRAPH_COMPLETION if SearchType is not None else None


def _require_sdk() -> None:
    """Guard: fail loudly if the Cognee SDK is not installed."""
    if cognee is None:  # pragma: no cover - only in SDK-less scaffold envs
        raise RuntimeError(
            "cognee SDK is not installed; the memory seam cannot operate. "
            "Install backend deps (cognee[fastembed]==1.2.2)."
        )


class CogneeClient:
    """Thin async wrapper around the Cognee SDK, scoped per-ticker dataset.

    Each method targets the dataset ``company_{ticker}``. Methods are coroutines
    because every Cognee operation is I/O- and/or compute-bound.
    """

    @staticmethod
    def _with_provenance(content: str, metadata: dict[str, Any] | None) -> str:
        """Prepend a delimited provenance header so citations survive into chunks.

        Cognee 1.2.2's ``add`` has no ``metadata`` kwarg, so citation fields
        (source_url, published_at, ...) are embedded as a machine-parseable header
        at the top of the ingested text and recovered from search results. See the
        "Metadata attachment" note in ``docs/spike-cognee-1.2.2.md``.
        """
        if not metadata:
            return content
        fields = [
            f"{key}={metadata[key]}"
            for key in ("source_url", "published_at", "source", "title")
            if metadata.get(key)
        ]
        if not fields:
            return content
        return "[PROVENANCE] " + " | ".join(fields) + "\n\n" + content

    @staticmethod
    def _result_to_dict(result: Any) -> dict[str, Any]:
        """Normalize a Cognee search/recall result into a JSON-safe dict.

        Results expose ``search_result`` (the hit payload / answer, a ``list[str]``)
        plus ``dataset_id`` / ``dataset_name`` (provenance). UUIDs are coerced to
        str. See ``docs/spike-cognee-1.2.2.md`` §2 for the runtime shape.
        """
        if hasattr(result, "model_dump"):
            data: dict[str, Any] = result.model_dump()
        elif isinstance(result, dict):
            data = dict(result)
        else:
            data = {"search_result": result}
        if data.get("dataset_id") is not None:
            data["dataset_id"] = str(data["dataset_id"])
        return data

    async def add(
        self, ticker: str, content: str, *, metadata: dict[str, Any] | None = None
    ) -> None:
        """Add normalized content to the ticker's dataset (``cognee.add``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            content: Normalized text to ingest.
            metadata: Citation metadata (source_url, published_at, ...), embedded
                as a provenance header (Cognee's ``add`` takes no metadata kwarg).
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        text = self._with_provenance(content, metadata)
        logger.debug("cognee.add", dataset=dataset, has_metadata=metadata is not None)
        await cognee.add(text, dataset_name=dataset, node_set=[dataset])

    async def cognify(self, ticker: str) -> None:
        """Build/update the per-company knowledge graph (``cognee.cognify``).

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        logger.debug("cognee.cognify", dataset=dataset)
        await cognee.cognify(datasets=[dataset])

    async def search(
        self,
        ticker: str,
        query: str,
        *,
        top_k: int = 10,
        session_id: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve a grounded answer from the ticker's dataset (``cognee.search``).

        Uses ``SearchType.GRAPH_COMPLETION`` (spike-verified). Cognee 1.2.2 has no
        ``dataset_name`` or ``filters`` param on ``search`` — scope is ``datasets=``.

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            query: The natural-language query.
            top_k: Maximum number of hits to consider.
            session_id: Optional session for session-aware retrieval / feedback
                (feeds the improve + session-memory work in issues #10/#11).
            filters: Reserved (e.g. date range). Cognee 1.2.2 has no native date
                filter; passing filters is a no-op here — see the spike doc.

        Returns:
            A list of result dicts (``search_result`` payload + dataset provenance).
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        if filters:
            logger.debug("cognee.search.filters_ignored", dataset=dataset, filters=filters)
        logger.debug("cognee.search", dataset=dataset, top_k=top_k)
        results = await cognee.search(
            query_text=query,
            query_type=_SEARCH_TYPE,
            datasets=[dataset],
            top_k=top_k,
            session_id=session_id,
        )
        return [self._result_to_dict(r) for r in results]

    async def recall(
        self,
        ticker: str,
        query: str,
        *,
        top_k: int = 10,
        session_id: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Auto-routed recall over the ticker's dataset (``cognee.recall``, V2).

        Spike verdict: ``recall`` is a real V2 primitive — a session-cache-aware
        wrapper over ``search`` that picks the ``SearchType`` for you
        (``auto_route=True``). Exposed here per the issue's correction.

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            query: The natural-language query.
            top_k: Maximum number of hits.
            session_id: Optional session id (session-memory work, #11).
            filters: Reserved; not applied (see :meth:`search`).

        Returns:
            A list of recalled entries as JSON-safe dicts.
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        logger.debug("cognee.recall", dataset=dataset)
        results = await cognee.recall(
            query_text=query,
            datasets=[dataset],
            top_k=top_k,
            session_id=session_id,
        )
        return [self._result_to_dict(r) for r in results]

    async def delete(self, ticker: str, *, filters: dict[str, Any] | None = None) -> None:
        """Purge the ticker's entire dataset (``cognee.forget``).

        Spike verdict: top-level ``cognee.delete`` is deprecated; the V2 unified
        deletion is ``forget(dataset="company_TICKER")`` for a whole-ticker purge.
        Sliced (date-bounded) deletion is not supported by this seam.

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            filters: If provided, raises — sliced delete is unsupported.

        Raises:
            NotImplementedError: If ``filters`` is provided (sliced delete).
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        if filters:
            raise NotImplementedError(
                "sliced delete is not supported by the cognee 1.2.2 seam; "
                "delete() purges the whole ticker dataset via forget()"
            )
        logger.debug("cognee.forget", dataset=dataset)
        await cognee.forget(dataset=dataset)


_client: CogneeClient | None = None


def get_cognee_client() -> CogneeClient:
    """Return the process-wide :class:`CogneeClient` singleton."""
    global _client
    if _client is None:
        _client = CogneeClient()
    return _client
