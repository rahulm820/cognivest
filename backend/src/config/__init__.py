"""Application configuration package.

Exposes the cached :class:`Settings` singleton and the structured-logging setup.
"""

from src.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
