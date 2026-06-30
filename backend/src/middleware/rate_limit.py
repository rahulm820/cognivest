"""Per-user rate limiting (Redis-backed).

A FastAPI dependency that throttles expensive endpoints (notably the LLM-backed
query path) using a per-user counter in Redis. Limit comes from
``settings.query_rate_limit_per_minute``.
"""

from __future__ import annotations

from fastapi import Depends

from src.middleware.auth_middleware import CurrentUser, get_current_user


class RateLimiter:
    """Sliding/fixed-window per-user rate limiter over Redis."""

    def __init__(self, *, limit_per_minute: int | None = None) -> None:
        """Configure the limiter (defaults to the settings value)."""
        self._limit_per_minute = limit_per_minute

    async def __call__(self, user: CurrentUser = Depends(get_current_user)) -> None:
        """Enforce the per-user rate limit for the current request.

        Raises:
            NotImplementedError: Always, in the scaffold phase.
        """
        # TODO(phase-6): INCR redis key f"rl:{user.id}:{minute}" with EXPIRE;
        #                raise HTTP 429 when the count exceeds the limit.
        raise NotImplementedError("TODO(phase-6): implement Redis per-user rate limiting")


# Default limiter instance for use as a route dependency.
rate_limit = RateLimiter()
