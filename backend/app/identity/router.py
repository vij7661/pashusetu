from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_farmer_registration, current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import BuyerProfile, FarmerProfile, FarmerRegistration
from app.identity.schemas import (
    BuyerProfileCreate,
    BuyerProfileResponse,
    FarmerKYCSubmit,
    FarmerProfileCreate,
    FarmerProfileResponse,
    FarmerRegistrationComplete,
    FarmerRegistrationDetails,
    FarmerRegistrationStatus,
)
from app.identity.service import (
    complete_farmer_registration_kyc,
    create_buyer_profile,
    create_farmer_profile,
    save_farmer_registration_details,
)

router = APIRouter(prefix="/identity", tags=["identity"])


def _registration_status(registration: FarmerRegistration) -> FarmerRegistrationStatus:
    next_step = "KYC" if registration.full_name else "FARMER_DETAILS"
    if registration.user_id is not None:
        next_step = "HOME"
    return FarmerRegistrationStatus(
        registration_id=registration.registration_code,
        registration_status=registration.status,
        next_step=next_step,
        full_name=registration.full_name,
        village=registration.village,
        mandal=registration.mandal,
        district=registration.district,
        state=registration.state,
        preferred_language=registration.preferred_language,
    )


@router.get("/farmer-registration/status", response_model=FarmerRegistrationStatus)
def farmer_registration_status(
    registration: FarmerRegistration = Depends(current_farmer_registration),
):
    return _registration_status(registration)


@router.put("/farmer-registration/details", response_model=FarmerRegistrationStatus)
def farmer_registration_details(
    payload: FarmerRegistrationDetails,
    db: Session = Depends(get_db),
    registration: FarmerRegistration = Depends(current_farmer_registration),
):
    registration = save_farmer_registration_details(db, registration, payload)
    return _registration_status(registration)


@router.post("/farmer-registration/kyc", response_model=FarmerRegistrationComplete)
def farmer_registration_kyc(
    payload: FarmerKYCSubmit,
    db: Session = Depends(get_db),
    registration: FarmerRegistration = Depends(current_farmer_registration),
):
    profile, tokens = complete_farmer_registration_kyc(
        db, registration, payload.aadhaar_number
    )
    return FarmerRegistrationComplete(
        farmer_id=profile.farmer_code,
        kyc_status=profile.kyc_status,
        registration_status="KYC_SUBMITTED",
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
    )


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
