from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from .config import TokenConfig
from .exceptions import MissingClaim, TokenExpired, TokenInvalid


def generate_token(payload: dict, config: TokenConfig) -> str:
    missing = [c for c in config.claims if c not in payload]
    if missing:
        raise MissingClaim(f"Missing required claims: {', '.join(missing)}")

    now = datetime.now(timezone.utc)
    jwt_payload = {
        **payload,
        "iat": now,
        "exp": now + timedelta(seconds=config.token_ttl_seconds),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(jwt_payload, config.secret_key, algorithm=config.algorithm)


def validate_token(token: str, config: TokenConfig) -> dict:
    try:
        return jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    except jwt.ExpiredSignatureError:
        raise TokenExpired("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise TokenInvalid(str(exc))
