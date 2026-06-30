"""Content-hash dedup gate.

Dedup happens BEFORE ``cognee.add()`` (a hard invariant). :func:`content_hash` is a
pure, deterministic function (fully implemented + unit-tested). :func:`is_duplicate`
consults the Postgres dedup ledger via the ingestion repository.
"""

from __future__ import annotations

import hashlib
import uuid

from src.collectors.base import NormalizedItem
from src.repositories.ingestion_repo import IngestionRepository


def content_hash(item: NormalizedItem) -> str:
    """Compute a stable SHA-256 hex digest for a normalized item.

    The hash is derived from the fields that define content identity (ticker,
    source URL, title, body) so semantically identical items collide and are
    deduped, while genuine updates (different body/url) produce a new hash.

    Args:
        item: The normalized item.

    Returns:
        A 64-character lowercase hex SHA-256 digest.
    """
    parts = [
        item.ticker.upper(),
        item.source_url or "",
        item.title.strip(),
        item.body.strip(),
    ]
    payload = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


async def is_duplicate(
    item: NormalizedItem,
    company_id: uuid.UUID,
    repo: IngestionRepository,
) -> bool:
    """Return True if this item was already ingested for the company.

    Args:
        item: The normalized item to check.
        company_id: The company's primary key.
        repo: The ingestion repository (dedup ledger access).

    Returns:
        Whether the item's content hash already exists for the company.
    """
    return await repo.exists_hash(company_id, content_hash(item))
