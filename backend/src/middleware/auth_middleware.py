"""JWT verification + RBAC dependencies.

FastAPI dependencies used by routers to enforce auth:
  * :func:`get_current_user` — verify an RS256 JWT and resolve the principal.
  * :func:`require_admin` — additionally require the ``admin`` role.
  * :func:`require_service_token` — guard internal ``/memory/*`` endpoints with the
    service-to-service token (ARCHITECTURE.md §9, §11).
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """The authenticated principal resolved from a JWT."""

    id: str
    email: str
    role: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    """Verify the bearer JWT and return the current user.

    Raises:
        HTTPException: 401 if the credentials are missing (scaffold behaviour).
        NotImplementedError: For the token-verification body, in the scaffold phase.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token"
        )
    # TODO(phase-1): decode_jwt(credentials.credentials) -> CurrentUser(id, email, role)
    raise NotImplementedError("TODO(phase-1): implement JWT verification in get_current_user")


async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require that the current user has the ``admin`` role.

    Raises:
        HTTPException: 403 if the user is not an admin.
    """
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin role required")
    return user


async def require_service_token(
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
) -> None:
    """Guard internal ``/memory/*`` endpoints with the service-to-service token.

    Raises:
        HTTPException: 401 if the token is missing.
        NotImplementedError: For the constant-time comparison, in the scaffold phase.
    """
    if x_service_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing service token"
        )
    # TODO(phase-1): constant-time compare x_service_token with settings.service_token
    raise NotImplementedError("TODO(phase-1): implement service-token verification")
