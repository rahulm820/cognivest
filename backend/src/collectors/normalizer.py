"""Normalization to the common item schema.

Maps heterogeneous vendor payloads onto :class:`NormalizedItem`
(title, body, source, ts, ticker, source_url). Keeping normalization separate from
fetching lets every vendor reuse the same dedup + ingestion path.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.collectors.base import NormalizedItem


def normalize(raw: dict[str, Any], *, ticker: str, source: str) -> NormalizedItem:
    """Map a single raw vendor record into a :class:`NormalizedItem`.

    Tolerant of both GDELT records (``title``/``url``/``seendate``/``domain``) and
    generic records (``body``/``published_at``/``source_url``); missing fields fall
    back sensibly so no record is dropped for shape alone.

    Args:
        raw: A single raw vendor record.
        ticker: The ticker the record belongs to.
        source: The vendor/source identifier (e.g. ``"gdelt"``).
    """
    title = str(raw.get("title") or "").strip() or "(untitled)"
    body = str(raw.get("body") or raw.get("content") or title).strip()
    url = raw.get("url") or raw.get("url_mobile") or raw.get("source_url")
    domain = raw.get("domain")
    ts = _parse_ts(raw.get("seendate") or raw.get("published_at") or raw.get("ts"))
    return NormalizedItem(
        ticker=ticker.upper(),
        title=title,
        body=body or title,
        source=str(domain or source),
        ts=ts,
        source_url=str(url) if url else None,
        extra={"vendor": source},
    )


def _parse_ts(value: Any) -> datetime:
    """Parse a vendor timestamp; default to 'now' (UTC) when absent/unparseable."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        # GDELT compact form: YYYYMMDDTHHMMSSZ
        try:
            return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)
