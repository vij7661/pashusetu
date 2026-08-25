from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Role
from app.core.errors import AppError
from app.identity.models import User, UserRole
from app.identity.profile_models import FarmerProfile, BuyerProfile
from app.identity.schemas import FarmerProfileCreate, BuyerProfileCreate


def _ensure_role(db: Session, user: User, role: Role) -> None:
    exists = db.scalar(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role == role.value)
    )
    if not exists:
        db.add(UserRole(user_id=user.id, role=role.value))


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
