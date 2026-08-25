from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import get_settings

ALGORITHM = "HS256"


def create_token(subject: str, token_type: str, expires_delta: timedelta, roles: list[str]) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_access_token(subject: str, roles: list[str]) -> str:
    settings = get_settings()
    return create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_minutes),
        roles,
    )


def create_refresh_token(subject: str, roles: list[str]) -> str:
    settings = get_settings()
    return create_token(
        subject,
        "refresh",
        timedelta(days=settings.refresh_token_days),
        roles,
    )


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
