"""Memory orchestration service — the ONLY caller of the Cognee client.

Every memory operation in the backend funnels through here. It wraps
``memory/cognee_client.py`` (the single Cognee seam) and exposes a clean, typed,
mockable surface to the rest of the app: ``ingest``, ``search``, ``answer``,
``assemble_context``, ``reflect``, ``delete``. No other module may touch the Cognee
client.

This service contains orchestration only — it does NOT reimplement retrieval,
embedding, reranking, or summarization (Cognee owns all of that). In particular the
query path is **single-LLM**: the answer text is Cognee's ``GRAPH_COMPLETION`` output
(see ``docs/spike-cognee-1.2.2.md`` §2/§4). There is no second answer-formatter LLM.
"""

from __future__ import annotations

from typing import Any

from src.config.logging import get_logger
from src.memory.cognee_client import CogneeClient, get_cognee_client
from src.schemas.common import DateRange
from src.schemas.memory import (
    MemoryAnswerOut,
    MemoryContextOut,
    MemorySearchOut,
    MemorySearchResult,
)
from src.schemas.query import Citation, GraphSnippet

logger = get_logger(__name__)


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
        """Add content to a ticker's dataset, then trigger the graph build.

        Orchestrates ``cognee.add`` followed by ``cognify`` (via :meth:`reflect`).
        This path is Celery-free: it awaits inline. Production queue-decoupling of
        ``cognify`` (CLAUDE.md §7.4) is deferred to the collection/worker issues and
        is not on the query path this service serves.
        """
        await self._client.add(ticker, content, metadata=metadata)
        await self.reflect(ticker)

    async def answer(
        self,
        ticker: str,
        question: str,
        *,
        date_range: DateRange | None = None,
        session_id: str | None = None,
        top_k: int = 10,
    ) -> MemoryAnswerOut:
        """Answer a natural-language question with a composed, grounded answer.

        Single-LLM: delegates to the seam's ``search`` (Cognee ``GRAPH_COMPLETION``),
        which returns a composed answer string — no separate LLM call. Citations are
        derived ONLY from real retrieval metadata; when none is available the answer is
        returned with an empty citation list rather than fabricated sources.

        Args:
            ticker: Company ticker; scoped to ``company_{ticker}`` by the seam.
            question: The user's natural-language question.
            date_range: Optional date filter, forwarded to the seam as opaque filters.
            session_id: Per-user session identity for future per-user memory
                (issues #10/#11). Held here for now — the frozen seam signatures do not
                yet accept it. TODO(seam-#4): forward to ``self._client.search`` once the
                additive ``session_id`` kwarg lands on the seam.
            top_k: Retrieval breadth passed to the seam.

        Returns:
            A :class:`MemoryAnswerOut` (answer + honest citations + graph snippet).
        """
        _ = session_id  # TODO(seam-#4): forward once the seam accepts session_id.
        results = await self._safe_search(ticker, question, top_k=top_k, date_range=date_range)
        answer_text = self._extract_answer(results)
        if not answer_text:
            return MemoryAnswerOut(answer=self._no_data_answer(ticker), citations=[])
        return MemoryAnswerOut(
            answer=answer_text,
            citations=self._extract_citations(results),
        )

    async def search(
        self,
        ticker: str,
        query: str,
        *,
        date_range: DateRange | None = None,
        top_k: int = 10,
    ) -> MemorySearchOut:
        """Retrieve ranked hits for a query scoped to a ticker's dataset.

        Best-effort mapping of the seam's result dicts onto ranked hits. The exact
        per-hit ``score``/reference shape is finalized by the real seam (issue #4);
        until then hits carry an honest default score and empty-metadata citations.
        """
        results = await self._safe_search(ticker, query, top_k=top_k, date_range=date_range)
        hits: list[MemorySearchResult] = []
        for index, item in enumerate(results, start=1):
            if not isinstance(item, dict):
                continue
            text = self._extract_answer([item])
            if not text:
                continue
            score = item.get("score")
            hits.append(
                MemorySearchResult(
                    text=text,
                    score=float(score) if isinstance(score, (int, float)) else 0.0,
                    citation=Citation(id=str(index), title=self._title_for(item, index)),
                )
            )
        return MemorySearchOut(results=hits)

    async def assemble_context(
        self,
        ticker: str,
        query: str,
        *,
        date_range: DateRange | None = None,
    ) -> MemoryContextOut:
        """Assemble a pre-LLM context block for a query.

        Under the single-LLM design there is no separate answer-formatter step, so the
        assembled ``context`` is Cognee's composed ``GRAPH_COMPLETION`` output — i.e. the
        same grounded text :meth:`answer` returns. Kept for the internal ``/memory/*``
        surface; the public query route uses :meth:`answer` directly.
        """
        result = await self.answer(ticker, query, date_range=date_range)
        return MemoryContextOut(context=result.answer, citations=result.citations)

    async def reflect(self, ticker: str) -> None:
        """Trigger a consolidation/cognify reflection pass for a ticker."""
        await self._client.cognify(ticker)

    async def delete(self, ticker: str, *, date_range: DateRange | None = None) -> None:
        """Purge a ticker's dataset or a date-bounded slice of it.

        Raises:
            NotImplementedError: Deletion belongs to the purge issue (#9); the seam's
                ``delete`` is a scaffold stub (and deprecated in Cognee 1.2.2 — spike
                CONTRADICTION #2). Out of scope for issue #5.
        """
        # TODO(#9): await self._client.delete(ticker, filters=...); prefer forget().
        raise NotImplementedError("TODO(#9): implement MemoryService.delete")

    # ------------------------------------------------------------------ helpers

    async def _safe_search(
        self,
        ticker: str,
        query: str,
        *,
        top_k: int,
        date_range: DateRange | None,
    ) -> list[dict[str, Any]]:
        """Call the seam, tolerating the scaffold stub so the query path never 500s.

        TODO(seam-#4): the Cognee seam is still a scaffold stub raising
        ``NotImplementedError``. Until it lands we treat that as "no data yet" (an empty
        result) rather than surfacing a 500 — the route must stay verifiable today.
        """
        filters = self._filters_from_date_range(date_range)
        try:
            results = await self._client.search(ticker, query, top_k=top_k, filters=filters)
        except NotImplementedError:
            logger.warning("memory.seam_not_implemented", ticker=ticker, op="search")
            return []
        return results or []

    @staticmethod
    def _filters_from_date_range(date_range: DateRange | None) -> dict[str, Any] | None:
        """Forward a date range to the seam's opaque ``filters`` dict.

        NOTE(#4): Cognee's ``search()`` has no native ``filters``/date param
        (spike CONTRADICTION #1); actual date-scoping (via TEMPORAL / query semantics)
        is the real seam's responsibility. We only pass the intent through.
        """
        if date_range is None:
            return None
        return {"from": date_range.from_.isoformat(), "to": date_range.to.isoformat()}

    @staticmethod
    def _extract_answer(results: list[dict[str, Any]]) -> str:
        """Pull the composed answer text out of the seam's result dicts.

        Primary shape (verified, spike §2): ``{"search_result": ["<answer>", ...]}``.
        Falls back to generic ``answer``/``text``/``content`` keys used by other
        SearchTypes, and tolerates bare strings.
        """
        parts: list[str] = []
        for item in results:
            if isinstance(item, str):
                if item.strip():
                    parts.append(item.strip())
                continue
            if not isinstance(item, dict):
                continue
            search_result = item.get("search_result")
            if isinstance(search_result, list):
                parts.extend(str(s).strip() for s in search_result if str(s).strip())
                continue
            if isinstance(search_result, str) and search_result.strip():
                parts.append(search_result.strip())
                continue
            for key in ("answer", "text", "content"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value.strip())
                    break
        return "\n\n".join(parts).strip()

    @staticmethod
    def _extract_citations(results: list[dict[str, Any]]) -> list[Citation]:
        """Build citations from real retrieval metadata only — never fabricated.

        Reads ``references``/``citations`` entries attached to a result. The frozen seam
        signature does not request ``include_references``, so today this is honestly
        empty; the extraction is forward-compatible for when issue #4 exposes references.
        """
        citations: list[Citation] = []
        index = 0
        for item in results:
            if not isinstance(item, dict):
                continue
            refs = item.get("references")
            if not isinstance(refs, list):
                refs = item.get("citations")
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if not isinstance(ref, dict):
                    continue
                index += 1
                url = ref.get("source_url") or ref.get("url")
                title = ref.get("title") or url or f"Source {index}"
                citations.append(
                    Citation(
                        id=str(index),
                        title=str(title),
                        url=url if isinstance(url, str) else None,
                        published_at=ref.get("published_at"),
                    )
                )
        return citations

    @staticmethod
    def _title_for(item: dict[str, Any], index: int) -> str:
        """Best-effort human label for a ranked hit's citation."""
        title = item.get("title") or item.get("source_url") or item.get("dataset_name")
        return str(title) if title else f"Source {index}"

    @staticmethod
    def _no_data_answer(ticker: str) -> str:
        """Honest answer shape when the dataset has no ingested data yet."""
        return (
            f"No data has been ingested yet for {ticker}, so there is nothing to answer "
            "from. Once price and news collection has run for this ticker, ask again."
        )


_service: MemoryService | None = None


def get_memory_service() -> MemoryService:
    """Return the process-wide :class:`MemoryService` singleton."""
    global _service
    if _service is None:
        _service = MemoryService()
    return _service
