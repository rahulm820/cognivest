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

import re
from typing import Any

# NOTE: This is the ONLY permitted Cognee import in the codebase.
# It is wrapped so the scaffold imports cleanly even if the SDK is absent.
try:  # pragma: no cover - import guard for scaffold environments
    import cognee  # type: ignore[import-untyped]
    from cognee.modules.data.exceptions import (  # type: ignore[import-untyped]
        DatasetNotFoundError,
    )
    from cognee.modules.search.types import SearchType  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    cognee = None  # type: ignore[assignment]
    SearchType = None  # type: ignore[assignment]
    DatasetNotFoundError = None  # type: ignore[assignment,misc]

from src.config.logging import get_logger
from src.memory.dataset_naming import dataset_name, user_dataset_name

logger = get_logger(__name__)

# Retrieval mode. GRAPH_COMPLETION is Cognee's default and the spike-verified path
# (docs/spike-cognee-1.2.2.md §4): vector + graph retrieval yielding a grounded,
# generated answer in ``result["search_result"]``. Kept internal so callers never
# depend on Cognee's ``SearchType``.
_SEARCH_TYPE = SearchType.GRAPH_COMPLETION if SearchType is not None else None

# Per-user memory retrieval (issue #11) uses CHUNKS: it returns the raw stored
# preference/history text via vector lookup WITHOUT a completion LLM, so pulling a
# user's context adds no second GRAPH_COMPLETION round-trip to the query path. User
# results are deliberately NOT run through the provenance/reference parser, so user
# memory can never surface as a news citation.
_USER_SEARCH_TYPE = SearchType.CHUNKS if SearchType is not None else None

# Provenance header markers. Citation fields are embedded as a delimited, terminated
# header at the top of each ingested document (Cognee's ``add`` has no metadata
# kwarg). The explicit closing marker matters: Cognee's Evidence block collapses all
# whitespace in the chunk snippet, so without a terminator the final ``title=`` field
# would bleed into the document body. Keep the emitter (``_with_provenance``) and the
# parser (``_parse_provenance``) in sync via these two constants.
_PROVENANCE_OPEN = "[PROVENANCE]"
_PROVENANCE_CLOSE = "[/PROVENANCE]"

# One provenance span: everything between the open and close markers (DOTALL so a span
# that survived across a newline still matches).
_PROVENANCE_RE = re.compile(
    re.escape(_PROVENANCE_OPEN) + r"(.*?)" + re.escape(_PROVENANCE_CLOSE),
    re.DOTALL,
)

# The ``Evidence:`` header Cognee appends (on its own line) when ``include_references``
# is set — see ``modules/retrieval/utils/references.py`` (``EVIDENCE_HEADER``). We split
# the answer here to keep the returned prose clean.
_EVIDENCE_HEADER = "Evidence:"
_EVIDENCE_SPLIT_RE = re.compile(rf"(?m)^[ \t]*{re.escape(_EVIDENCE_HEADER)}[ \t]*$")

# Provenance fields we recognize; only these keys are lifted into a citation.
_CITATION_FIELDS = ("title", "source_url", "published_at")


def _is_no_data_error(exc: BaseException) -> bool:
    """True when a search error means 'nothing ingested yet', not a real fault.

    ``cognee.search`` surfaces "no data" in three shapes on a fresh/empty store, all of
    which we map to an empty result so the query path returns an honest "no data yet"
    200 instead of a 500 (spike-verified, fact (a)):

    1. Unknown/empty dataset -> ``DatasetNotFoundError("No datasets found.")``.
    2. Cognee's own precondition guard converts ``DatabaseNotCreatedError`` /
       ``UserNotFoundError`` into a ``CogneeValidationError`` named
       ``"SearchPreconditionError"`` (matched by ``.name`` to avoid importing it).
    3. Deeper fresh-store case: that guard does NOT catch the raw
       ``OperationalError: unable to open database file`` raised by ``get_default_user``
       when the sqlite store was never created. We recognize it structurally (class
       name + message) so we do not import sqlalchemy into the seam, and so genuinely
       broken stores (locked / corrupt DB) still propagate as a real 500.

    Any other error is a genuine fault and must keep propagating.
    """
    if DatasetNotFoundError is not None and isinstance(exc, DatasetNotFoundError):
        return True
    if getattr(exc, "name", None) in {"SearchPreconditionError", "DatasetNotFoundError"}:
        return True
    return (
        type(exc).__name__ == "OperationalError"
        and "unable to open database file" in str(exc)
    )


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

        The header is bounded by an explicit ``[/PROVENANCE]`` terminator. Cognee's
        Evidence block (``include_references=True``) renders each cited chunk as a
        whitespace-collapsed snippet, so without the terminator the trailing
        ``title=`` value would run straight into the document body. The terminator
        gives :meth:`_parse_provenance` a clean right boundary for every field.
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
        header = f"{_PROVENANCE_OPEN} " + " | ".join(fields) + f" {_PROVENANCE_CLOSE}"
        return header + "\n\n" + content

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

    # ------------------------------------------------------- reference parsing
    #
    # Cognee 1.2.2's ``include_references=True`` does NOT return a structured
    # references key. For ``GRAPH_COMPLETION`` (str answers) it appends a free-text
    # ``Evidence:`` block into the answer string, whose bullets quote the cited
    # chunks — including the ``[PROVENANCE] … [/PROVENANCE]`` header we embed at
    # ingestion. So we recover citations by (1) splitting the Evidence block out of
    # the answer prose and (2) parsing the provenance headers back into dicts. These
    # helpers are pure and unit-testable.

    @staticmethod
    def _split_evidence(text: str) -> tuple[str, str]:
        """Split an answer string into (clean prose, evidence block).

        Cognee appends the Evidence block as ``"<answer>\\n\\nEvidence:\\n- …"``. We
        cut at the ``Evidence:`` header line so the returned answer stays clean prose.
        If there is no Evidence block the whole string is the answer.
        """
        parts = _EVIDENCE_SPLIT_RE.split(text, maxsplit=1)
        if len(parts) == 2:
            return parts[0].rstrip(), parts[1]
        return text, ""

    @staticmethod
    def _strip_provenance(text: str) -> str:
        """Remove any residual ``[PROVENANCE] … [/PROVENANCE]`` spans from prose.

        Belt-and-suspenders: provenance normally lives only inside the (stripped)
        Evidence block, but if the header were ever echoed into the answer this keeps
        the returned prose clean.
        """
        return _PROVENANCE_RE.sub("", text).strip()

    @staticmethod
    def _provenance_fields(span: str, *, terminated: bool) -> dict[str, str]:
        """Lift recognized ``key=value`` pairs out of one provenance span body.

        Fields are ``key=value`` pairs joined by ``|``. For an un-terminated span (its
        ``[/PROVENANCE]`` was truncated away by Cognee's snippet cap) the trailing
        segment carries no closing delimiter, so it may be a value cut mid-way — it is
        dropped rather than emitted half-cut. Only a segment that a delimiter proved
        complete is trusted. ``source_url``/``published_at`` are emitted *before*
        ``title`` (see :meth:`_with_provenance`), so they survive truncation.
        """
        segments = span.split("|")
        if not terminated and segments:
            segments = segments[:-1]
        fields: dict[str, str] = {}
        for segment in segments:
            key, sep, value = segment.partition("=")
            if not sep:
                continue
            key = key.strip()
            value = value.strip()
            if key in _CITATION_FIELDS and value:
                fields.setdefault(key, value)
        return fields

    @staticmethod
    def _parse_provenance(text: str) -> list[dict[str, str]]:
        """Parse ``[PROVENANCE] key=value | … [/PROVENANCE]`` spans into dicts.

        Returns one ``{title, source_url, published_at}`` dict per span, keeping only
        recognized, non-empty fields.

        Cognee's Evidence block renders each cited chunk as a snippet capped at ~160
        chars, which routinely truncates the header's trailing ``[/PROVENANCE]`` (and a
        tail of the last ``title=`` value) away. So a span is bounded by its
        ``[/PROVENANCE]`` terminator when present, otherwise by the next span, a quote/
        newline Evidence-bullet boundary, or end-of-text. For an un-terminated span the
        final (possibly half-cut) field is dropped — never emitted mid-value — while the
        earlier complete pairs (``source_url``/``published_at``, emitted first) survive.
        This is what keeps citations non-empty on real, truncated Evidence.
        """
        if not text or _PROVENANCE_OPEN not in text:
            return []
        refs: list[dict[str, str]] = []
        open_len = len(_PROVENANCE_OPEN)
        idx = 0
        while True:
            start = text.find(_PROVENANCE_OPEN, idx)
            if start == -1:
                break
            body_start = start + open_len
            close = text.find(_PROVENANCE_CLOSE, body_start)
            next_open = text.find(_PROVENANCE_OPEN, body_start)
            terminated = close != -1 and (next_open == -1 or close < next_open)
            if terminated:
                span = text[body_start:close]
                idx = close + len(_PROVENANCE_CLOSE)
            else:
                end = next_open if next_open != -1 else len(text)
                span = text[body_start:end]
                # An un-terminated header has no explicit right edge, so stop at the
                # first quote/newline: the Evidence-bullet delimiter that bounds it.
                boundary = re.search(r'["\n\r]', span)
                if boundary:
                    span = span[: boundary.start()]
                idx = end
            fields = CogneeClient._provenance_fields(span, terminated=terminated)
            ref = {key: fields[key] for key in _CITATION_FIELDS if key in fields}
            if ref:
                refs.append(ref)
        return refs

    @staticmethod
    def _dedupe_references(refs: list[dict[str, str]]) -> list[dict[str, str]]:
        """Drop duplicate citations, keyed by source_url (falling back to title)."""
        seen: set[str] = set()
        deduped: list[dict[str, str]] = []
        for ref in refs:
            key = ref.get("source_url") or ref.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(ref)
        return deduped

    def _attach_references(self, data: dict[str, Any]) -> dict[str, Any]:
        """Clean the answer text and attach parsed citations under ``references``.

        For every ``search_result`` string: parse its provenance headers, strip the
        Evidence block (and any stray provenance) out of the answer prose, and collect
        the citations. The deduped list is exposed under the ``references`` key that
        ``MemoryService._extract_citations`` reads. Non-string payloads are left as-is.
        """
        search_result = data.get("search_result")
        if not isinstance(search_result, list):
            return data
        cleaned: list[Any] = []
        references: list[dict[str, str]] = []
        for entry in search_result:
            if not isinstance(entry, str):
                cleaned.append(entry)
                continue
            references.extend(self._parse_provenance(entry))
            answer_text, _evidence = self._split_evidence(entry)
            cleaned.append(self._strip_provenance(answer_text))
        data["search_result"] = cleaned
        if references:
            data["references"] = self._dedupe_references(references)
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

        Calls Cognee with ``include_references=True`` and post-processes each result:
        the free-text ``Evidence:`` block is split OUT of the answer prose and the
        embedded ``[PROVENANCE]`` headers are parsed into structured citations exposed
        under a ``references`` key (Cognee 1.2.2 returns no structured references key
        of its own). The returned ``search_result`` text is clean prose.

        No-data resilience: an unknown/empty dataset or a fresh, uninitialized store
        makes Cognee raise (see :func:`_is_no_data_error` for the exact signatures);
        we map those to ``[]`` so the query path returns an honest "no data yet" 200
        rather than a 500. Every other error is re-raised.

        Args:
            ticker: The company ticker; resolved to ``company_{ticker}``.
            query: The natural-language query.
            top_k: Maximum number of hits to consider.
            session_id: Optional session for session-aware retrieval / feedback
                (feeds the improve + session-memory work in issues #10/#11).
            filters: Reserved (e.g. date range). Cognee 1.2.2 has no native date
                filter; passing filters is a no-op here — see the spike doc.

        Returns:
            A list of result dicts (clean ``search_result`` prose + dataset provenance
            + a ``references`` list of citation dicts when provenance was recovered).
            Empty when the ticker's dataset has no ingested data yet.
        """
        _require_sdk()
        dataset = dataset_name(ticker)
        if filters:
            logger.debug("cognee.search.filters_ignored", dataset=dataset, filters=filters)
        logger.debug("cognee.search", dataset=dataset, top_k=top_k)
        try:
            results = await cognee.search(
                query_text=query,
                query_type=_SEARCH_TYPE,
                datasets=[dataset],
                top_k=top_k,
                session_id=session_id,
                include_references=True,
            )
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is a no-data signal
            # Only the specifically-recognized "no data ingested yet" signatures are
            # swallowed (-> honest 200); every genuine fault is re-raised (-> 500).
            if _is_no_data_error(exc):
                logger.info("cognee.search.no_data", dataset=dataset)
                return []
            raise
        return [self._attach_references(self._result_to_dict(r)) for r in results]

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

        Idempotent: forgetting a dataset that was never created (or an already-empty
        store) is a no-op success — the "no data" signatures are swallowed so the
        forget lifecycle (issue #9) is safe to run against a fresh ticker. Every
        other error propagates.

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
        try:
            await cognee.forget(dataset=dataset)
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is a no-data signal
            if _is_no_data_error(exc):
                logger.info("cognee.forget.no_data", dataset=dataset)
                return
            raise

    # ---------------------------------------------------- per-user memory (#11)
    #
    # These are ADDITIVE, parallel to the per-ticker methods above. They target the
    # ``user_{id}`` dataset family (see ``dataset_naming.user_dataset_name``) instead
    # of ``company_{ticker}``, keeping per-user session memory strictly isolated from
    # per-company memory. They do NOT change any existing method's signature.

    async def add_user_memory(
        self, user_id: str, content: str, *, metadata: dict[str, Any] | None = None
    ) -> None:
        """Add per-user session memory to the user's dataset (``cognee.add``).

        Mirrors :meth:`add` but targets ``user_{id}``. Used for stated preferences
        and Q&A-interaction history. Preferences are stored WITHOUT citation metadata
        (they are not sources), so they cannot masquerade as a news citation.

        Args:
            user_id: Raw ``X-User-Id``; resolved to ``user_{id}`` (sanitized).
            content: Normalized text to remember for this user.
            metadata: Optional provenance header fields (normally unused for user
                memory).
        """
        _require_sdk()
        dataset = user_dataset_name(user_id)
        text = self._with_provenance(content, metadata)
        logger.debug("cognee.add.user", dataset=dataset, has_metadata=metadata is not None)
        await cognee.add(text, dataset_name=dataset, node_set=[dataset])

    async def cognify_user(self, user_id: str) -> None:
        """Build/update a user's session-memory graph (``cognee.cognify``).

        Mirrors :meth:`cognify` but targets ``user_{id}``. Callers run this OFF the
        query path (detached background task) because cognify is ~30-60s.

        Args:
            user_id: Raw ``X-User-Id``; resolved to ``user_{id}`` (sanitized).
        """
        _require_sdk()
        dataset = user_dataset_name(user_id)
        logger.debug("cognee.cognify.user", dataset=dataset)
        await cognee.cognify(datasets=[dataset])

    async def search_user_memory(
        self,
        user_id: str,
        query: str,
        *,
        top_k: int = 5,
        session_id: str | None = None,
    ) -> list[str]:
        """Retrieve raw per-user memory chunks from ``user_{id}`` (``cognee.search``).

        Uses ``SearchType.CHUNKS`` (no completion LLM) and returns the raw stored
        text chunks, so pulling a user's context is cheap and adds no second
        GRAPH_COMPLETION round-trip. Results are intentionally NOT passed through the
        provenance/reference parser: user memory must never become a citation.

        No-data resilience: a brand-new user (dataset absent) or a fresh, uninitialized
        store raises the same "no data" signatures as :meth:`search`; those map to an
        empty list so a first-time / unknown user simply yields no personalization
        context rather than a 500. Every other error re-raises.

        Args:
            user_id: Raw ``X-User-Id``; resolved to ``user_{id}`` (sanitized).
            query: Retrieval query (e.g. a fixed "user's stated interests" probe).
            top_k: Maximum number of chunks to return.
            session_id: Optional session id, forwarded for session-aware retrieval.

        Returns:
            A list of raw memory-chunk strings (empty when the user has no memory yet).
        """
        _require_sdk()
        dataset = user_dataset_name(user_id)
        logger.debug("cognee.search.user", dataset=dataset, top_k=top_k)
        try:
            results = await cognee.search(
                query_text=query,
                query_type=_USER_SEARCH_TYPE,
                datasets=[dataset],
                top_k=top_k,
                session_id=session_id,
            )
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is a no-data signal
            if _is_no_data_error(exc):
                logger.info("cognee.search.user.no_data", dataset=dataset)
                return []
            raise
        chunks: list[str] = []
        for result in results:
            data = self._result_to_dict(result)
            payload = data.get("search_result")
            if isinstance(payload, list):
                chunks.extend(str(entry).strip() for entry in payload if str(entry).strip())
            elif isinstance(payload, str) and payload.strip():
                chunks.append(payload.strip())
        return chunks


_client: CogneeClient | None = None


def get_cognee_client() -> CogneeClient:
    """Return the process-wide :class:`CogneeClient` singleton."""
    global _client
    if _client is None:
        _client = CogneeClient()
    return _client
