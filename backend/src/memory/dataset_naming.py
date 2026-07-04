"""Per-ticker Cognee dataset naming.

One Cognee dataset per company: ``dataset_name = f"company_{ticker}"``. This is a
hard invariant — price and news for a ticker share the *same* dataset so the graph
can correlate them, and queries are naturally scoped per company.

This module is intentionally pure (no Cognee import) and fully functional so it can
be unit-tested directly.
"""

from __future__ import annotations

import hashlib
import re

DATASET_PREFIX = "company_"
_TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")

# --- Per-user dataset naming (issue #11) --------------------------------------
# A second, parallel dataset family ``user_{id}`` holds per-user session memory
# (stated preferences + Q&A history), kept strictly separate from the per-company
# ``company_{ticker}`` datasets. Same hard-isolation invariant: a user's memory is
# only ever queried under their own dataset name, never cross-user.
USER_DATASET_PREFIX = "user_"
# ``X-User-Id`` is arbitrary, untrusted header input. It is NEVER interpolated raw
# into a dataset name — it is normalized to this restricted charset first.
_USER_ID_MAX_LEN = 64
_USER_ID_SAFE_RE = re.compile(r"[^a-z0-9_-]+")
_USER_ID_STRIP = "-_"


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


def normalize_user_id(user_id: str) -> str:
    """Normalize an arbitrary ``X-User-Id`` header into a safe dataset segment.

    The raw header is untrusted and NEVER interpolated into a dataset name. This
    normalizer is:

      * **deterministic** — the same header always maps to the same id across
        sessions (this is what makes per-user memory persist between requests);
      * **charset-restricted** — output is lowercase ``[a-z0-9_-]`` only;
      * **length-capped** — at most :data:`_USER_ID_MAX_LEN` chars;
      * **collision-safe** — if sanitizing changed the string or it exceeded the
        cap, a short stable ``sha256(raw)[:8]`` suffix is appended so distinct raw
        ids can never collapse onto the same dataset (``alice`` stays ``alice``;
        ``alice@corp.com`` -> ``alice-corp-com-<hash>``).

    Args:
        user_id: Raw ``X-User-Id`` header value.

    Returns:
        A safe, stable id segment for use in :func:`user_dataset_name`.

    Raises:
        ValueError: If ``user_id`` is empty/blank.
    """
    if not user_id or not user_id.strip():
        raise ValueError("user id must be a non-empty string")
    raw = user_id.strip()
    lowered = raw.lower()
    cleaned = _USER_ID_SAFE_RE.sub("-", lowered).strip(_USER_ID_STRIP)
    if cleaned != lowered or len(cleaned) > _USER_ID_MAX_LEN:
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
        base = cleaned[: _USER_ID_MAX_LEN - 9].strip(_USER_ID_STRIP) or "u"
        return f"{base}-{digest}"
    return cleaned


def user_dataset_name(user_id: str) -> str:
    """Return the Cognee dataset name for a user's session memory.

    Args:
        user_id: Raw ``X-User-Id`` header value (sanitized internally).

    Returns:
        ``f"user_{normalized_id}"``.
    """
    return f"{USER_DATASET_PREFIX}{normalize_user_id(user_id)}"


def user_id_from_dataset(name: str) -> str:
    """Inverse of :func:`user_dataset_name`: extract the id from a user dataset name.

    Args:
        name: A dataset name produced by :func:`user_dataset_name`.

    Returns:
        The normalized user-id portion.

    Raises:
        ValueError: If ``name`` does not use the expected prefix.
    """
    if not name.startswith(USER_DATASET_PREFIX):
        raise ValueError(f"{name!r} is not a valid user dataset name")
    return name[len(USER_DATASET_PREFIX) :]
