"""Date/time helpers for range handling."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta


def utcnow() -> datetime:
    """Return the current timezone-aware UTC time."""
    return datetime.now(UTC)


def days_ago(days: int) -> date:
    """Return the date ``days`` days before today (UTC).

    Args:
        days: Number of days to subtract.
    """
    return (utcnow() - timedelta(days=days)).date()


def parse_range_str(range_str: str) -> int:
    """Parse a simple range string like ``"30d"`` into a day count.

    Args:
        range_str: A string of the form ``<n>d`` (e.g. ``"7d"``, ``"30d"``).

    Returns:
        The number of days.

    Raises:
        ValueError: If the string is not in the ``<n>d`` form.
    """
    s = range_str.strip().lower()
    if not s.endswith("d") or not s[:-1].isdigit():
        raise ValueError(f"invalid range {range_str!r}: expected '<n>d', e.g. '30d'")
    return int(s[:-1])
