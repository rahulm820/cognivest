"""Request identity dependencies — HACKATHON BYPASS (issue #6).

> ⚠️ **This is a hackathon identity mechanism, NOT authentication.**
> The scaffold assumed RS256 JWT (PEM keypairs) + Google OAuth + refresh rotation.
> For the 2.5-day build we deliberately gut that ceremony from the runtime path
> and assert identity with a single header, ``X-User-Id`` (default ``demo-user``).
> The JWT/OAuth code and the login page are left in place but bypassed — restore
> real auth before anything ships. Per-user session memory (#10/#11) only needs a
> stable user id, which the header provides.

FastAPI dependencies used by routers:
  * :func:`get_current_user` — resolve the caller from the ``X-User-Id`` header.
  * :func:`require_admin` — RBAC gate (kept; the bypass user is an admin).
  * :func:`require_service_token` — internal ``/memory/*`` guard (no-op in bypass).
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

# Default identity when no header is sent — keeps every route callable with no token.
_DEFAULT_USER_ID = "demo-user"


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """The current principal. In bypass mode, asserted by the ``X-User-Id`` header."""

    id: str
    email: str
    role: str


async def get_current_user(
    x_user_id: str = Header(default=_DEFAULT_USER_ID, alias="X-User-Id"),
) -> CurrentUser:
    """Resolve the current principal from the ``X-User-Id`` header.

    HACKATHON IDENTITY MECHANISM, NOT AUTHENTICATION (issue #6): the caller asserts
    its identity via a header; there is no token verification. Missing header →
    ``demo-user``. The bypass principal is given the ``admin`` role so the single
    demo user can reach every route (RBAC is effectively off for the hackathon).

    Args:
        x_user_id: The asserted user id (``X-User-Id`` header; defaults to ``demo-user``).

    Returns:
        A :class:`CurrentUser` for the asserted id.
    """
    return CurrentUser(id=x_user_id, email=f"{x_user_id}@cognivest.local", role="admin")


async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require the ``admin`` role.

    Kept for API shape; in bypass mode :func:`get_current_user` returns ``admin``,
    so this passes for the demo user.

    Raises:
        HTTPException: 403 if the user is not an admin.
    """
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin role required")
    return user


async def require_service_token() -> None:
    """Internal ``/memory/*`` guard — NO-OP in hackathon bypass (issue #6).

    The scaffold gated internal endpoints with a service-to-service token. For the
    hackathon runtime path we bypass it (Cognee is internal/network-isolated in the
    demo). HACKATHON MECHANISM, NOT AUTHENTICATION — restore before prod.
    """
    return None
