"""Generic async repository base.

Provides the common CRUD seam over an :class:`AsyncSession` for a single ORM model.
Concrete repositories subclass this and add model-specific queries. This is the ONLY
layer permitted to construct SQL.
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async data-access object for a single model type."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to a request-scoped session.

        Args:
            session: The async SQLAlchemy session.
        """
        self.session = session

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        """Fetch a single entity by primary key, or ``None`` if absent."""
        return await self.session.get(self.model, entity_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """List entities with simple pagination."""
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        """Stage a new entity for insertion and flush to obtain its PK."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Stage an entity for deletion."""
        await self.session.delete(entity)
