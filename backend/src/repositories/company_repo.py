"""Company data access."""

from __future__ import annotations

from src.models.company import Company
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Postgres data access for :class:`Company`."""

    model = Company

    async def get_by_ticker(self, ticker: str) -> Company | None:
        """Fetch a company by its (unique) ticker.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): select(Company).where(Company.ticker == ticker.upper())
        raise NotImplementedError("TODO(phase-1): implement CompanyRepository.get_by_ticker")

    async def list_for_user(self, user_id: object) -> list[Company]:
        """List companies on a given user's watchlist (join WATCHLIST_ITEMS).

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): join companies <- watchlist_items where user_id == user_id
        raise NotImplementedError("TODO(phase-1): implement CompanyRepository.list_for_user")
