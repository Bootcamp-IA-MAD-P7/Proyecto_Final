"""Signed tokens: HS256 with AUTH_SECRET, checking signature, expiry, audience and issuer."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.auth.principal import Principal, Role
from app.settings import Settings

ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    """Missing, expired, badly signed or malformed token. Its reason is never sent to the client."""


def issue_token(settings: Settings, principal: Principal, ttl_seconds: int | None = None) -> str:
    if not settings.auth_secret:
        raise InvalidTokenError("AUTH_SECRET is not configured")
    now = datetime.now(UTC)
    ttl = settings.auth_dev_token_ttl_seconds if ttl_seconds is None else ttl_seconds
    claims = {
        "sub": principal.subject,
        "role": principal.role.value,
        "aud": settings.auth_audience,
        "iss": settings.auth_issuer,
        "iat": now,
        "exp": now + timedelta(seconds=ttl),
    }
    return jwt.encode(claims, settings.auth_secret, algorithm=ALGORITHM)


def verify_token(settings: Settings, token: str) -> Principal:
    if not settings.auth_secret:
        raise InvalidTokenError("AUTH_SECRET is not configured")
    try:
        claims = jwt.decode(
            token,
            settings.auth_secret,
            algorithms=[ALGORITHM],
            audience=settings.auth_audience,
            issuer=settings.auth_issuer,
            options={"require": ["sub", "exp", "aud", "iss"]},
        )
        return Principal(subject=str(claims["sub"]), role=Role(claims.get("role")))
    except (jwt.PyJWTError, ValueError) as error:
        raise InvalidTokenError(type(error).__name__) from error
