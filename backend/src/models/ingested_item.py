"""Dedup ledger. Mirrors §4.5 INGESTED_ITEMS.

The ``content_hash`` is UNIQUE PER COMPANY — this is the O(1) dedup check performed
*before* ``cognee.add()`` so duplicate content is never re-ingested/re-cognified.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDMixin


class IngestedItem(UUIDMixin, Base):
    """Record that a piece of content was ingested for a company (dedup key)."""

    __tablename__ = "ingested_items"
    __table_args__ = (
        UniqueConstraint("company_id", "content_hash", name="uq_ingested_company_hash"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
