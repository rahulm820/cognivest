"""Structured logging configuration (structlog).

Centralises logging setup so every layer (API, workers, collectors) emits
consistent, JSON-friendly structured logs. Call :func:`configure_logging` once at
process start (done by the app factory and the Celery app).
"""

from __future__ import annotations

import logging

import structlog

from src.config.settings import Settings, get_settings


def configure_logging(settings: Settings | None = None) -> None:
    """Configure stdlib logging + structlog processors.

    In production, render JSON; in development, render a human-friendly console.

    Args:
        settings: Optional settings override; falls back to the cached singleton.
    """
    settings = settings or get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(format="%(message)s", level=level)

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]
    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer()
        if settings.is_production
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger.

    Args:
        name: Optional logger name (usually ``__name__``).
    """
    return structlog.get_logger(name)
