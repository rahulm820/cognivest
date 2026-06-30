"""Data-access layer.

ALL Postgres SQL lives here — services and routers must never run SQL directly.
Each repository wraps an :class:`~sqlalchemy.ext.asyncio.AsyncSession`.
"""

from src.repositories.base import BaseRepository
from src.repositories.company_repo import CompanyRepository
from src.repositories.ingestion_repo import IngestionRepository
from src.repositories.user_repo import UserRepository

__all__ = [
    "BaseRepository",
    "CompanyRepository",
    "IngestionRepository",
    "UserRepository",
]
