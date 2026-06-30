"""Per-ticker Cognee dataset naming.

One Cognee dataset per company: ``dataset_name = f"company_{ticker}"``. This is a
hard invariant — price and news for a ticker share the *same* dataset so the graph
can correlate them, and queries are naturally scoped per company.

This module is intentionally pure (no Cognee import) and fully functional so it can
be unit-tested directly.
"""

from __future__ import annotations

import re

DATASET_PREFIX = "company_"
_TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


def normalize_ticker(ticker: str) -> str:
    """Normalize a raw ticker to canonical form (trimmed, uppercased).

    Args:
        ticker: Raw ticker string.

    Returns:
        The canonical uppercase ticker.

    Raises:
        ValueError: If the ticker is empty or fails format validation.
    """
    if not ticker or not ticker.strip():
        raise ValueError("ticker must be a non-empty string")
    candidate = ticker.strip().upper()
    if not _TICKER_RE.match(candidate):
        raise ValueError(
            f"invalid ticker {ticker!r}: must be 1-10 chars of A-Z, 0-9, '.', '-' "
            "and start with a letter"
        )
    return candidate


def dataset_name(ticker: str) -> str:
    """Return the Cognee dataset name for a ticker.

    Args:
        ticker: Raw or canonical ticker (validated + uppercased internally).

    Returns:
        ``f"company_{TICKER}"``.
    """
    return f"{DATASET_PREFIX}{normalize_ticker(ticker)}"


def ticker_from_dataset(name: str) -> str:
    """Inverse of :func:`dataset_name`: extract the ticker from a dataset name.

    Args:
        name: A dataset name produced by :func:`dataset_name`.

    Returns:
        The ticker portion.

    Raises:
        ValueError: If ``name`` does not use the expected prefix.
    """
    if not name.startswith(DATASET_PREFIX):
        raise ValueError(f"{name!r} is not a valid company dataset name")
    return name[len(DATASET_PREFIX) :]
