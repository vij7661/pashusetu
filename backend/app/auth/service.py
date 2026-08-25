from datetime import datetime, timedelta, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import Role
from app.core.errors import AppError
from app.core.security import create_access_token, create_refresh_token
from app.identity.models import OTPChallenge, User, UserRole
from app.auth.providers import DevelopmentOTPProvider

DEV_OTP = "4816"


def _hash_otp(otp: str) -> str:
    return sha256(otp.encode("utf-8")).hexdigest()


def request_otp(db: Session, mobile_e164: str, purpose: str) -> None:
    settings = get_settings()
    challenge = OTPChallenge(
        mobile_e164=mobile_e164,
        purpose=purpose,
        otp_hash=_hash_otp(DEV_OTP),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.otp_ttl_seconds),
    )
    db.add(challenge)
    db.commit()
    DevelopmentOTPProvider().send(mobile_e164, DEV_OTP)


def verify_otp(db: Session, mobile_e164: str, otp: str, purpose: str) -> tuple[User, list[str]]:
    settings = get_settings()
    challenge = db.scalar(
        select(OTPChallenge)
        .where(
            OTPChallenge.mobile_e164 == mobile_e164,
            OTPChallenge.purpose == purpose,
            OTPChallenge.consumed.is_(False),
        )
        .order_by(OTPChallenge.created_at.desc())
    )
    if not challenge:
        raise AppError("OTP_NOT_FOUND", "No active OTP challenge.", 400)
    if challenge.expires_at < datetime.now(timezone.utc):
        raise AppError("OTP_EXPIRED", "OTP has expired.", 400)
    if challenge.attempts >= settings.otp_max_attempts:
        raise AppError("OTP_ATTEMPTS_EXCEEDED", "Too many OTP attempts.", 429)

    challenge.attempts += 1
    if challenge.otp_hash != _hash_otp(otp):
        db.commit()
        raise AppError("OTP_INVALID", "Invalid OTP.", 400)

    challenge.consumed = True
    user = db.scalar(select(User).where(User.mobile_e164 == mobile_e164))
    if user is None:
        user = User(mobile_e164=mobile_e164)
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role=Role.FARMER.value))

    db.commit()
    db.refresh(user)
    roles = [r.role for r in user.roles]
    return user, roles


def tokens_for(user: User, roles: list[str]) -> dict:
    return {
        "access_token": create_access_token(str(user.id), roles),
        "refresh_token": create_refresh_token(str(user.id), roles),
        "token_type": "bearer",
    }
