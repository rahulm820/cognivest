"""Watchlist service: add/list/remove companies for a user.

Orchestrates the company + watchlist repositories and triggers backfill on add. Holds
no SQL itself — all data access goes through repositories.
"""

from __future__ import annotations

import uuid

from src.repositories.company_repo import CompanyRepository
from src.schemas.company import CompanyOut, TickerCreate


class WatchlistService:
    """Business logic for managing a user's watchlist of tickers."""

    def __init__(self, company_repo: CompanyRepository) -> None:
        """Bind to the company repository."""
        self._company_repo = company_repo

    async def add_ticker(self, user_id: uuid.UUID, payload: TickerCreate) -> CompanyOut:
        """Add a ticker to the user's watchlist and enqueue initial backfill.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): upsert company, create watchlist item, enqueue backfill job
        raise NotImplementedError("TODO(phase-1): implement WatchlistService.add_ticker")

    async def list_companies(self, user_id: uuid.UUID) -> list[CompanyOut]:
        """List the companies on a user's watchlist.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): repo.list_for_user(user_id) -> [CompanyOut]
        raise NotImplementedError("TODO(phase-1): implement WatchlistService.list_companies")

    async def remove_ticker(self, user_id: uuid.UUID, ticker: str) -> None:
        """Remove a ticker from the user's watchlist.

        Does NOT purge Cognee memory (separate admin action — ARCHITECTURE.md §5.5).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): delete watchlist item for (user_id, company by ticker)
        raise NotImplementedError("TODO(phase-1): implement WatchlistService.remove_ticker")
