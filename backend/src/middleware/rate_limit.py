"""Per-user rate limiting — NO-OP pass-through for the hackathon (issue #6).

The scaffold planned a Redis-backed per-user throttle on the LLM query path. For
the 2.5-day build this is a **pass-through**: it resolves the caller (so the
dependency shape is unchanged) and returns without enforcing any limit. Real
Redis limiting (``INCR``/``EXPIRE`` + HTTP 429) is a later, phase-6 concern.
"""

from __future__ import annotations

from fastapi import Depends

from src.middleware.auth_middleware import CurrentUser, get_current_user


class RateLimiter:
    """Per-user rate limiter. Currently a no-op pass-through (see module docstring)."""

    def __init__(self, *, limit_per_minute: int | None = None) -> None:
        """Configure the limiter (defaults to the settings value; unused while no-op)."""
        self._limit_per_minute = limit_per_minute

    async def __call__(self, user: CurrentUser = Depends(get_current_user)) -> None:
        """No-op: resolve the caller and allow the request through.

        TODO(phase-6): INCR redis key f"rl:{user.id}:{minute}" with EXPIRE and
        raise HTTP 429 when the count exceeds ``self._limit_per_minute``.
        """
        return None


# Default limiter instance for use as a route dependency.
rate_limit = RateLimiter()
