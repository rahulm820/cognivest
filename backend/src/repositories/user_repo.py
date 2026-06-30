"""User data access."""

from __future__ import annotations

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Postgres data access for :class:`User`."""

    model = User

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by (unique) email.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-1): select(User).where(User.email == email)
        raise NotImplementedError("TODO(phase-1): implement UserRepository.get_by_email")
