"""Natural-language query request/response schemas.

The query path wraps ``cognee.search()``/``recall()`` scoped to a single
company dataset, then formats a cited answer via the LLM (see ``ai/``).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.schemas.common import DateRange

# All request/response models on the query path serialize with camelCase aliases so
# the wire shape matches the frontend contract in ``frontend/src/types/api.ts``
# exactly (e.g. ``published_at`` -> ``publishedAt``, ``graph_snippet`` -> ``graphSnippet``,
# incoming ``dateRange`` -> ``date_range``). ``populate_by_name=True`` keeps snake_case
# construction working inside the backend. FastAPI serializes response models
# ``by_alias=True`` by default, so no per-route flag is needed.
_camel = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class QueryRequest(BaseModel):
    """A user's natural-language question scoped to a company + optional dates."""

    model_config = _camel

    question: str = Field(min_length=1, max_length=2000)
    date_range: DateRange | None = Field(
        default=None, description="Optional date filter applied during retrieval."
    )


class Citation(BaseModel):
    """A source citation backing part of the answer.

    Field names mirror ``Citation`` in ``frontend/src/types/api.ts``. Note ``url`` and
    ``published_at`` are nullable here even though the TS type marks them required:
    citations are only ever populated from real retrieval metadata (never fabricated),
    so honest ``null`` wins over a made-up value. See GATE 2 flag for the frontend fix.
    """

    model_config = _camel

    id: str = Field(
        description="Citation id — the 1-based index referenced in the answer text, as a string."
    )
    title: str
    url: str | None = None
    published_at: datetime | None = None


class GraphSnippet(BaseModel):
    """A small slice of the per-company knowledge graph supporting the answer."""

    model_config = _camel

    nodes: list[dict[str, object]] = Field(default_factory=list)
    edges: list[dict[str, object]] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """The cited answer returned to the client."""

    model_config = _camel

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    graph_snippet: GraphSnippet = Field(default_factory=GraphSnippet)
