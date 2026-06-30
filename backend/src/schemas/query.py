"""Natural-language query request/response schemas.

The query path wraps ``cognee.search()``/``recall()`` scoped to a single
company dataset, then formats a cited answer via the LLM (see ``ai/``).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.common import DateRange


class QueryRequest(BaseModel):
    """A user's natural-language question scoped to a company + optional dates."""

    question: str = Field(min_length=1, max_length=2000)
    date_range: DateRange | None = Field(
        default=None, description="Optional date filter applied during retrieval."
    )


class Citation(BaseModel):
    """A source citation backing part of the answer."""

    index: int = Field(description="1-based citation index referenced in the answer text.")
    title: str
    url: str | None = None
    published_at: datetime | None = None


class GraphSnippet(BaseModel):
    """A small slice of the per-company knowledge graph supporting the answer."""

    nodes: list[dict[str, object]] = Field(default_factory=list)
    edges: list[dict[str, object]] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """The cited answer returned to the client."""

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    graph_snippet: GraphSnippet = Field(default_factory=GraphSnippet)
