"""Company data access."""

from __future__ import annotations

from sqlalchemy import select

from src.models.company import Company
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Postgres data access for :class:`Company`."""

    model = Company

    async def get_by_ticker(self, ticker: str) -> Company | None:
        """Fetch a company by its (unique) ticker, or ``None`` if absent."""
        result = await self.session.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, ticker: str, *, name: str | None = None) -> Company:
        """Return the company for ``ticker``, creating it if it does not exist.

        Used by the backfill path so collecting a not-yet-watchlisted ticker still
        has a company row to hang the dedup ledger + ingestion jobs off.
        """
        existing = await self.get_by_ticker(ticker)
        if existing is not None:
            return existing
        return await self.add(Company(ticker=ticker.upper(), name=name))

    async def list_for_user(self, user_id: object) -> list[Company]:
        """List companies on a given user's watchlist (join WATCHLIST_ITEMS).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): join companies <- watchlist_items where user_id == user_id
        raise NotImplementedError("TODO(phase-1): implement CompanyRepository.list_for_user")
