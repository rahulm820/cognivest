"""Price collector (market-data vendor, pluggable).

Fetches OHLCV bars for a ticker and normalizes each into a text summary item so
price action lands in the SAME Cognee dataset as news (enabling correlation).
"""

from __future__ import annotations

from src.collectors.base import Collector, NormalizedItem


class PriceCollector(Collector):
    """Collect price bars from the configured market-data vendor."""

    name = "price"

    async def collect(self, ticker: str) -> list[NormalizedItem]:
        """Fetch price bars and normalize to summary items.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-2): call market-data vendor, map OHLCV bars -> NormalizedItem
        raise NotImplementedError("TODO(phase-2): implement PriceCollector.collect")
