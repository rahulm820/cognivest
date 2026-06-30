"""News/web collector (news API + web-search vendors, pluggable).

Pulls per-company articles/web content via licensed news APIs and a web-search API
(no unrestricted scraping) and normalizes them to the common item schema.
"""

from __future__ import annotations

from src.collectors.base import Collector, NormalizedItem


class NewsCollector(Collector):
    """Collect news/web content from the configured news + search vendors."""

    name = "news"

    async def collect(self, ticker: str) -> list[NormalizedItem]:
        """Fetch articles/web hits and normalize to items.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-2): query news + web-search vendors -> NormalizedItem list
        raise NotImplementedError("TODO(phase-2): implement NewsCollector.collect")
