"""Internal memory-layer schemas (the ``/memory/*`` service surface).

These mirror the Cognee-backed wrapper surface described in ARCHITECTURE.md §5.7.
All ``/memory/*`` endpoints are internal-only (service token + network isolation).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.schemas.common import DateRange
from src.schemas.query import Citation, GraphSnippet


class MemoryStore(BaseModel):
    """Request to ingest a normalized item into a company's dataset."""

    ticker: str = Field(description="Ticker the content belongs to.")
    content: str = Field(description="Normalized text content to add to Cognee.")
    source_url: str | None = None
    content_hash: str | None = Field(
        default=None, description="Precomputed dedup hash; if absent it is derived."
    )


class MemorySearch(BaseModel):
    """Request to retrieve from a company's dataset."""

    ticker: str
    query: str = Field(min_length=1)
    date_range: DateRange | None = None
    top_k: int = Field(default=10, ge=1, le=100)


class MemorySearchResult(BaseModel):
    """A single ranked retrieval hit."""

    text: str
    score: float
    citation: Citation


class MemorySearchOut(BaseModel):
    """Ranked retrieval results for a search request."""

    results: list[MemorySearchResult] = Field(default_factory=list)


class MemoryContext(BaseModel):
    """Request to assemble a pre-LLM context block for a query."""

    ticker: str
    query: str = Field(min_length=1)
    date_range: DateRange | None = None


class MemoryContextOut(BaseModel):
    """Assembled context block ready for prompt injection."""

    context: str
    citations: list[Citation] = Field(default_factory=list)
    graph_snippet: GraphSnippet = Field(default_factory=GraphSnippet)


class MemoryAnswerOut(BaseModel):
    """A composed, grounded answer to a company query.

    Single-LLM design: the ``answer`` text is produced directly by Cognee's
    ``GRAPH_COMPLETION`` search (no separate answer-formatter LLM). Distinct from
    ``MemorySearchOut`` (ranked hits, no composed answer) and ``MemoryContextOut``
    (a pre-LLM context block) — neither fits a single grounded answer, hence this type.
    Maps 1:1 onto ``schemas.query.QueryResponse``.
    """

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    graph_snippet: GraphSnippet = Field(default_factory=GraphSnippet)


class MemoryReflection(BaseModel):
    """Request to trigger a consolidation/cognify reflection pass."""

    ticker: str


class MemoryDelete(BaseModel):
    """Request to purge a dataset or a date-bounded slice of it."""

    ticker: str
    date_range: DateRange | None = Field(
        default=None, description="If omitted, the whole dataset is purged."
    )


class MemoryAck(BaseModel):
    """Generic acknowledgement for write/delete memory operations."""

    ok: bool = True
    dataset_name: str
    detail: str | None = None
