"""Normalization to the common item schema.

Maps heterogeneous vendor payloads onto :class:`NormalizedItem`
(title, body, source, ts, ticker, source_url). Keeping normalization separate from
fetching lets every vendor reuse the same dedup + ingestion path.
"""

from __future__ import annotations

from typing import Any

from src.collectors.base import NormalizedItem


def normalize(raw: dict[str, Any], *, ticker: str, source: str) -> NormalizedItem:
    """Map a single raw vendor record into a :class:`NormalizedItem`.

    Args:
        raw: A single raw vendor record.
        ticker: The ticker the record belongs to.
        source: The vendor/source identifier.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-2): map raw payload fields -> NormalizedItem(title, body, ts, url, ...)
    raise NotImplementedError("TODO(phase-2): implement normalizer.normalize")
