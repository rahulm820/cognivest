"""Security primitives: password hashing and RS256 JWT encode/decode.

Phase 0 scaffold: signatures + docstrings are in place; bodies raise
``NotImplementedError`` with ``# TODO(phase-1)`` markers. Real implementations use
``passlib`` (bcrypt) for passwords and ``python-jose`` for RS256 JWTs, with keys
loaded from the paths in settings (``JWT_PRIVATE_KEY_PATH`` / ``JWT_PUBLIC_KEY_PATH``).
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): return passlib bcrypt hash of `password`.
    raise NotImplementedError("TODO(phase-1): implement bcrypt password hashing")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): return passlib bcrypt verify(password, password_hash).
    raise NotImplementedError("TODO(phase-1): implement bcrypt password verification")


def encode_jwt(
    claims: dict[str, Any],
    *,
    expires_in: timedelta,
    private_key: str | None = None,
) -> str:
    """Encode and RS256-sign a JWT with the given claims and expiry.

    Args:
        claims: Token claims (e.g. ``sub``, ``role``).
        expires_in: Lifetime added to ``iat`` to compute ``exp``.
        private_key: PEM private key; defaults to the key at the configured path.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): jose.jwt.encode(claims | exp/iat, private_key, algorithm="RS256").
    raise NotImplementedError("TODO(phase-1): implement RS256 JWT encoding")


def decode_jwt(token: str, *, public_key: str | None = None) -> dict[str, Any]:
    """Verify and decode an RS256 JWT, returning its claims.

    Args:
        token: The encoded JWT.
        public_key: PEM public key; defaults to the key at the configured path.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): jose.jwt.decode(token, public_key, algorithms=["RS256"]).
    raise NotImplementedError("TODO(phase-1): implement RS256 JWT decoding")
