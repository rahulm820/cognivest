"""Authentication request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials for password login."""

    email: EmailStr
    password: str = Field(min_length=1, repr=False)


class RefreshRequest(BaseModel):
    """Refresh-token rotation request."""

    refresh_token: str = Field(repr=False)


class TokenPair(BaseModel):
    """Issued access + refresh token pair (RS256 JWT)."""

    access_token: str = Field(repr=False)
    refresh_token: str = Field(repr=False)
    token_type: str = "bearer"
    expires_in: int = Field(description="Access-token lifetime in seconds.")
