"""SQLAlchemy 2.x ORM models.

The schema mirrors the ER diagram in ARCHITECTURE.md §4.5. Importing this package
registers every model on :class:`Base.metadata` so Alembic autogenerate sees them.
"""

from src.models.base import Base
from src.models.company import Company
from src.models.ingested_item import IngestedItem
from src.models.ingestion_job import IngestionJob
from src.models.query_log import QueryLog
from src.models.user import User
from src.models.watchlist_item import WatchlistItem

__all__ = [
    "Base",
    "Company",
    "IngestedItem",
    "IngestionJob",
    "QueryLog",
    "User",
    "WatchlistItem",
]
