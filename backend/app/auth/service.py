from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.providers import DevelopmentOTPProvider
from app.core.config import get_settings
from app.core.enums import Role
from app.core.errors import AppError
from app.core.security import create_access_token, create_refresh_token, create_registration_token
from app.identity.models import OTPChallenge, User, UserRole
from app.identity.profile_models import FarmerProfile, FarmerRegistration

OTP_LENGTH = 4
FARMER_LOGIN_PURPOSE = "FARMER_LOGIN"
FARMER_REGISTRATION_PURPOSE = "FARMER_REGISTRATION"
DEVELOPMENT_ENVS = {"local", "test", "development"}


def _hash_otp(otp: str) -> str:
    return sha256(otp.encode("utf-8")).hexdigest()


def _development_otp(mobile_e164: str) -> str:
    settings = get_settings()
    digest = sha256(
        f"{settings.development_otp_seed}:{mobile_e164}".encode("utf-8")
    ).hexdigest()
    value = int(digest[:8], 16) % (10**OTP_LENGTH)
    return f"{value:0{OTP_LENGTH}d}"


def request_otp(db: Session, mobile_e164: str, purpose: str) -> None:
    settings = get_settings()
    if settings.app_env.lower() not in DEVELOPMENT_ENVS:
        raise AppError(
            "OTP_PROVIDER_NOT_CONFIGURED",
            "A production OTP provider must be configured before pilot/production use.",
            503,
        )

    otp = _development_otp(mobile_e164)
    challenge = OTPChallenge(
        mobile_e164=mobile_e164,
        purpose=purpose,
        otp_hash=_hash_otp(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.otp_ttl_seconds),
    )
    db.add(challenge)
    db.commit()
    DevelopmentOTPProvider().send(mobile_e164, otp)


def _consume_valid_otp(db: Session, mobile_e164: str, otp: str, purpose: str) -> None:
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
    db.commit()


def verify_otp(db: Session, mobile_e164: str, otp: str, purpose: str) -> tuple[User, list[str]]:
    _consume_valid_otp(db, mobile_e164, otp, purpose)

    user = db.scalar(select(User).where(User.mobile_e164 == mobile_e164))
    if purpose == FARMER_LOGIN_PURPOSE:
        if user is None:
            raise AppError("FARMER_NOT_REGISTERED", "No registered farmer account for this mobile.", 404)
        profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
        if profile is None:
            raise AppError("FARMER_NOT_REGISTERED", "No registered farmer account for this mobile.", 404)
    elif user is None:
        # Preserve the legacy generic LOGIN behavior for non-Farmer clients until
        # those registration flows are migrated. Farmer mobile never uses it.
        user = User(mobile_e164=mobile_e164)
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role=Role.FARMER.value))

    db.commit()
    db.refresh(user)
    roles = [r.role for r in user.roles]
    return user, roles


def verify_farmer_registration_otp(
    db: Session, mobile_e164: str, otp: str
) -> tuple[FarmerRegistration, str, str]:
    _consume_valid_otp(db, mobile_e164, otp, FARMER_REGISTRATION_PURPOSE)

    existing_user = db.scalar(select(User).where(User.mobile_e164 == mobile_e164))
    if existing_user is not None:
        profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == existing_user.id))
        if profile is not None:
            raise AppError(
                "FARMER_ALREADY_REGISTERED",
                "This mobile already belongs to a registered farmer. Use Existing Farmer login.",
                409,
            )

    registration = db.scalar(
        select(FarmerRegistration).where(FarmerRegistration.mobile_e164 == mobile_e164)
    )
    if registration is None:
        registration = FarmerRegistration(
            registration_code=f"REG-{uuid4().hex[:10].upper()}",
            mobile_e164=mobile_e164,
            status="NEW_IN_PROGRESS",
        )
        db.add(registration)
        db.flush()

    if registration.user_id is not None:
        raise AppError(
            "FARMER_ALREADY_REGISTERED",
            "Registration has already been converted to a farmer account.",
            409,
        )

    db.commit()
    db.refresh(registration)
    next_step = "KYC" if registration.full_name else "FARMER_DETAILS"
    token = create_registration_token(str(registration.id))
    return registration, token, next_step


def tokens_for(user: User, roles: list[str]) -> dict:
    return {
        "access_token": create_access_token(str(user.id), roles),
        "refresh_token": create_refresh_token(str(user.id), roles),
        "token_type": "bearer",
    }
