"""Per-user rate limiting (Redis-backed).

A FastAPI dependency that throttles expensive endpoints (notably the LLM-backed
query path) with a per-user fixed-window counter in Redis. The window is one
minute; the key ``rl:{user_id}:{minute}`` is ``INCR``'d and given a 60s TTL on
first use, and the request is rejected with HTTP 429 once the count exceeds the
limit (``settings.query_rate_limit_per_minute``, overridable per instance).

Fails **open**: if Redis is unreachable the request is allowed (with a warning),
so a cache outage degrades to "no limiting" rather than a hard outage.
"""

from __future__ import annotations

import time

from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.config.logging import get_logger
from src.config.settings import get_settings
from src.middleware.auth_middleware import CurrentUser, get_current_user

logger = get_logger(__name__)

_WINDOW_SECONDS = 60

_redis: Redis | None = None


def _get_redis() -> Redis:
    """Return the process-wide async Redis client (lazy singleton)."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(str(get_settings().redis_url), decode_responses=True)
    return _redis


class RateLimiter:
    """Fixed-window per-user rate limiter over Redis."""

    def __init__(self, *, limit_per_minute: int | None = None) -> None:
        """Configure the limiter. Defaults to ``query_rate_limit_per_minute``."""
        self._limit_per_minute = limit_per_minute

    @property
    def _limit(self) -> int:
        """Effective per-minute limit (instance override or settings default)."""
        return self._limit_per_minute or get_settings().query_rate_limit_per_minute

    async def __call__(self, user: CurrentUser = Depends(get_current_user)) -> None:
        """Enforce the per-user rate limit for the current request.

        Args:
            user: The current principal (from the identity dependency).

        Raises:
            HTTPException: 429 if the caller exceeded the per-minute limit.
        """
        limit = self._limit
        window = int(time.time()) // _WINDOW_SECONDS
        key = f"rl:{user.id}:{window}"
        try:
            count = await _get_redis().incr(key)
            if count == 1:
                await _get_redis().expire(key, _WINDOW_SECONDS)
        except RedisError as exc:  # fail open — never block on a cache outage
            logger.warning("rate_limit.redis_unavailable", error=str(exc), user_id=user.id)
            return None
        if count > limit:
            logger.info("rate_limit.exceeded", user_id=user.id, count=count, limit=limit)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"rate limit exceeded: {limit} requests/minute",
                headers={"Retry-After": str(_WINDOW_SECONDS)},
            )
        return None


# Default limiter instance for use as a route dependency.
rate_limit = RateLimiter()
