"""Auth routes: login + refresh.

Thin handlers — validate via schema, delegate to the auth/security layer, return a
schema. No business logic here.
"""

from __future__ import annotations

from fastapi import APIRouter, status

from src.schemas.auth import LoginRequest, RefreshRequest, TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest) -> TokenPair:
    """Authenticate by email/password and issue an RS256 JWT pair.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): delegate to auth service: verify credentials -> issue token pair
    raise NotImplementedError("TODO(phase-1): implement auth.login")


@router.post("/refresh", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def refresh(payload: RefreshRequest) -> TokenPair:
    """Rotate a refresh token into a new access + refresh pair.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): verify + rotate refresh token -> new TokenPair
    raise NotImplementedError("TODO(phase-1): implement auth.refresh")
