from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.service import tokens_for
from app.core.enums import Role
from app.core.errors import AppError
from app.identity.models import User, UserRole
from app.identity.profile_models import BuyerProfile, FarmerProfile, FarmerRegistration
from app.identity.schemas import BuyerProfileCreate, FarmerProfileCreate, FarmerRegistrationDetails


def _ensure_role(db: Session, user: User, role: Role) -> None:
    exists = db.scalar(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role == role.value)
    )
    if not exists:
        db.add(UserRole(user_id=user.id, role=role.value))


def save_farmer_registration_details(
    db: Session, registration: FarmerRegistration, payload: FarmerRegistrationDetails
) -> FarmerRegistration:
    if registration.user_id is not None:
        raise AppError("REGISTRATION_COMPLETE", "Farmer registration is already complete.", 409)
    registration.full_name = payload.full_name
    registration.village = payload.village
    registration.mandal = payload.mandal
    registration.district = payload.district
    registration.state = payload.state
    registration.preferred_language = payload.preferred_language
    registration.status = "NEW_IN_PROGRESS"
    db.commit()
    db.refresh(registration)
    return registration


def complete_farmer_registration_kyc(
    db: Session, registration: FarmerRegistration, aadhaar_number: str
) -> tuple[FarmerProfile, dict]:
    if not registration.full_name:
        raise AppError(
            "FARMER_DETAILS_REQUIRED",
            "Farmer details must be completed before KYC submission.",
            409,
        )

    if registration.user_id is not None:
        user = db.get(User, registration.user_id)
        profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == registration.user_id))
        if user is None or profile is None:
            raise AppError("REGISTRATION_STATE_INVALID", "Completed registration is inconsistent.", 500)
        return profile, tokens_for(user, [r.role for r in user.roles])

    existing_user = db.scalar(select(User).where(User.mobile_e164 == registration.mobile_e164))
    if existing_user is not None:
        existing_profile = db.scalar(
            select(FarmerProfile).where(FarmerProfile.user_id == existing_user.id)
        )
        if existing_profile is not None:
            raise AppError(
                "FARMER_ALREADY_REGISTERED",
                "This mobile already belongs to a registered farmer.",
                409,
            )

    # Raw Aadhaar is deliberately not persisted. The reference represents the
    # KYC submission event/provider hand-off and is safe to retain operationally.
    _ = aadhaar_number
    kyc_reference = f"KYC-{uuid4().hex[:12].upper()}"

    user = existing_user or User(
        mobile_e164=registration.mobile_e164,
        preferred_language=registration.preferred_language,
        status="ACTIVE",
    )
    if existing_user is None:
        db.add(user)
        db.flush()
    else:
        user.preferred_language = registration.preferred_language

    _ensure_role(db, user, Role.FARMER)

    profile = FarmerProfile(
        user_id=user.id,
        farmer_code=f"PS-F-{uuid4().hex[:8].upper()}",
        full_name=registration.full_name,
        village=registration.village,
        mandal=registration.mandal,
        district=registration.district,
        state=registration.state,
        kyc_status="KYC_PENDING",
        kyc_reference=kyc_reference,
        payout_status="PENDING",
    )
    db.add(profile)
    db.flush()

    registration.kyc_reference = kyc_reference
    registration.user_id = user.id
    registration.status = "KYC_SUBMITTED"

    db.commit()
    db.refresh(user)
    db.refresh(profile)
    db.refresh(registration)
    return profile, tokens_for(user, [r.role for r in user.roles])


def create_farmer_profile(db: Session, user: User, payload: FarmerProfileCreate) -> FarmerProfile:
    existing = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if existing:
        raise AppError("FARMER_PROFILE_EXISTS", "Farmer profile already exists.", 409)

    user.preferred_language = payload.preferred_language
    _ensure_role(db, user, Role.FARMER)

    profile = FarmerProfile(
        user_id=user.id,
        farmer_code=f"PS-F-{uuid4().hex[:8].upper()}",
        full_name=payload.full_name,
        village=payload.village,
        mandal=payload.mandal,
        district=payload.district,
        state=payload.state,
        latitude=str(payload.latitude) if payload.latitude is not None else None,
        longitude=str(payload.longitude) if payload.longitude is not None else None,
        kyc_status="KYC_PENDING",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def create_buyer_profile(db: Session, user: User, payload: BuyerProfileCreate) -> BuyerProfile:
    existing = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user.id))
    if existing:
        raise AppError("BUYER_PROFILE_EXISTS", "Buyer profile already exists.", 409)

    user.preferred_language = payload.preferred_language
    _ensure_role(db, user, Role.BUYER)

    profile = BuyerProfile(
        user_id=user.id,
        buyer_code=f"PS-B-{uuid4().hex[:8].upper()}",
        business_name=payload.business_name,
        contact_person=payload.contact_person,
        buyer_type=payload.buyer_type,
        city=payload.city,
        state=payload.state,
        latitude=str(payload.latitude) if payload.latitude is not None else None,
        longitude=str(payload.longitude) if payload.longitude is not None else None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
