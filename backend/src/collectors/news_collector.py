"""News/web collector — GDELT DOC 2.0 (keyless, issue #8).

Pulls per-company articles from GDELT's public DOC API (no API key, no scraping)
and normalizes them to the common item schema. The collector sits behind the
:class:`Collector` protocol, so a curated corpus (issue #17) or a keyed news API
can be swapped in without touching the ingestion pipeline.

GDELT ``ArtList`` returns headline-level records (title/url/domain/seendate) — no
full article body — so ingested news items are headline-grounded.
"""

from __future__ import annotations

import httpx

from src.collectors.base import Collector, NormalizedItem
from src.collectors.normalizer import normalize
from src.config.logging import get_logger

logger = get_logger(__name__)

_GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class NewsCollector(Collector):
    """Collect per-company news headlines from GDELT."""

    name = "news"

    def __init__(
        self, *, company_name: str | None = None, days: int = 30, max_records: int = 25
    ) -> None:
        """Configure the query window and breadth.

        Args:
            company_name: Human company name for a better query (e.g. "Apple Inc.");
                falls back to the ticker symbol when absent.
            days: Trailing lookback window.
            max_records: Cap on returned articles.
        """
        self._company_name = company_name
        self._days = days
        self._max_records = max_records

    def _query(self, ticker: str) -> str:
        """Build a GDELT query scoped to the company."""
        if self._company_name:
            return f'"{self._company_name}" OR {ticker}'
        return ticker

    async def collect(self, ticker: str) -> list[NormalizedItem]:
        """Fetch recent articles for ``ticker`` and normalize them.

        Returns an empty list on any vendor/network error (never raises) so a news
        outage cannot break a backfill run.
        """
        ticker = ticker.upper()
        params = {
            "query": self._query(ticker),
            "mode": "ArtList",
            "format": "json",
            "maxrecords": str(self._max_records),
            "timespan": f"{self._days}d",
            "sort": "DateDesc",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(_GDELT_URL, params=params)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("news.fetch_failed", ticker=ticker, error=str(exc))
            return []

        articles = payload.get("articles") or []
        items: list[NormalizedItem] = []
        for raw in articles:
            if not isinstance(raw, dict):
                continue
            # Prefer English-language records for the LLM path when language is present.
            if raw.get("language") and str(raw["language"]).lower() not in ("english", "en"):
                continue
            items.append(normalize(raw, ticker=ticker, source="gdelt"))
        logger.info("news.collected", ticker=ticker, count=len(items))
        return items
