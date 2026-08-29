from typing import Literal

from pydantic import BaseModel, Field

from app.identity.constants import PILOT_FARMER_STATE

SupportedLanguage = Literal["te", "hi", "en", "mr", "ta", "ml"]


class FarmerRegistrationDetails(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = PILOT_FARMER_STATE
    preferred_language: SupportedLanguage = "te"


class FarmerRegistrationStatus(BaseModel):
    registration_id: str
    registration_status: str
    next_step: str
    full_name: str | None = None
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    preferred_language: str


class FarmerKYCSubmit(BaseModel):
    # The raw Aadhaar value is validated for this request only and is not persisted.
    aadhaar_number: str = Field(pattern=r"^\d{12}$")


class FarmerRegistrationComplete(BaseModel):
    farmer_id: str
    kyc_status: str
    registration_status: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class FarmerProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = PILOT_FARMER_STATE
    latitude: float | None = None
    longitude: float | None = None
    preferred_language: SupportedLanguage = "te"


class FarmerProfileResponse(BaseModel):
    farmer_id: str
    full_name: str
    village: str | None
    mandal: str | None
    district: str | None
    state: str | None
    kyc_status: str
    payout_status: str
    preferred_language: str


class FarmerDashboardResponse(BaseModel):
    farmer_id: str
    kyc_status: str
    transaction_enabled: bool
    live_listings: int
    active_offers: int
    settled_amount_paise: int


class BuyerProfileCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    contact_person: str | None = None
    buyer_type: Literal["INDIVIDUAL_RETAILER", "PROPRIETORSHIP", "COMPANY", "BULK_BUYER", "OTHER"]
    city: str | None = None
    state: str | None = "Telangana"
    latitude: float | None = None
    longitude: float | None = None
    preferred_language: SupportedLanguage = "te"


class BuyerProfileResponse(BaseModel):
    buyer_id: str
    business_name: str
    contact_person: str | None
    buyer_type: str
    city: str | None
    state: str | None
    kyc_status: str
    business_verified: bool
    preferred_language: str
