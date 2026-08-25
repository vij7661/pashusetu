from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile, BuyerProfile
from app.identity.schemas import (
    FarmerProfileCreate,
    FarmerProfileResponse,
    BuyerProfileCreate,
    BuyerProfileResponse,
)
from app.identity.service import create_farmer_profile, create_buyer_profile

router = APIRouter(prefix="/identity", tags=["identity"])


@router.post("/farmers", response_model=FarmerProfileResponse, status_code=201)
def create_farmer(
    payload: FarmerProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    p = create_farmer_profile(db, user, payload)
    return FarmerProfileResponse(
        farmer_id=p.farmer_code,
        full_name=p.full_name,
        village=p.village,
        mandal=p.mandal,
        district=p.district,
        state=p.state,
        kyc_status=p.kyc_status,
        payout_status=p.payout_status,
        preferred_language=user.preferred_language,
    )


@router.get("/farmers/me", response_model=FarmerProfileResponse)
def get_farmer_me(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    p = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if not p:
        raise AppError("FARMER_PROFILE_NOT_FOUND", "Farmer profile not found.", 404)
    return FarmerProfileResponse(
        farmer_id=p.farmer_code,
        full_name=p.full_name,
        village=p.village,
        mandal=p.mandal,
        district=p.district,
        state=p.state,
        kyc_status=p.kyc_status,
        payout_status=p.payout_status,
        preferred_language=user.preferred_language,
    )


@router.post("/buyers", response_model=BuyerProfileResponse, status_code=201)
def create_buyer(
    payload: BuyerProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    p = create_buyer_profile(db, user, payload)
    return BuyerProfileResponse(
        buyer_id=p.buyer_code,
        business_name=p.business_name,
        contact_person=p.contact_person,
        buyer_type=p.buyer_type,
        city=p.city,
        state=p.state,
        kyc_status=p.kyc_status,
        business_verified=p.business_verified,
        preferred_language=user.preferred_language,
    )


@router.get("/buyers/me", response_model=BuyerProfileResponse)
def get_buyer_me(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    p = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user.id))
    if not p:
        raise AppError("BUYER_PROFILE_NOT_FOUND", "Buyer profile not found.", 404)
    return BuyerProfileResponse(
        buyer_id=p.buyer_code,
        business_name=p.business_name,
        contact_person=p.contact_person,
        buyer_type=p.buyer_type,
        city=p.city,
        state=p.state,
        kyc_status=p.kyc_status,
        business_verified=p.business_verified,
        preferred_language=user.preferred_language,
    )
