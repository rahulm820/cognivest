"""The Cognee boundary.

This package is the ONLY place the Cognee SDK may be imported — specifically
``cognee_client.py``. ``dataset_naming.py`` owns the per-ticker dataset naming
convention. Callers outside this package must go through
``services/memory_service.py``.
"""

from src.memory.dataset_naming import dataset_name

__all__ = ["dataset_name"]
