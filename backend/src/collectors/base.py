"""Collector interface + the common normalized item schema.

Vendors (market-data, news, web-search) are pluggable behind the
:class:`Collector` protocol. A collector fetches raw vendor payloads and yields
:class:`NormalizedItem` records; nothing downstream knows which vendor produced them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class NormalizedItem:
    """Common schema every collector normalizes to before dedup + ingestion."""

    ticker: str
    title: str
    body: str
    source: str
    ts: datetime
    source_url: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Collector(Protocol):
    """Pluggable vendor collector.

    Implementations fetch raw data for a ticker and return normalized items.
    """

    name: str

    async def collect(self, ticker: str) -> list[NormalizedItem]:
        """Fetch and normalize items for ``ticker``.

        Args:
            ticker: The company ticker to collect for.

        Returns:
            A list of normalized items ready for dedup + ingestion.
        """
        ...
