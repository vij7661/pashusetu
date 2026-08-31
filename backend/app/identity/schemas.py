from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.identity.constants import PILOT_FARMER_STATE

SupportedLanguage = Literal["te", "hi", "en", "mr", "ta", "ml"]
FarmerKYCStatus = Literal[
    "KYC_PENDING",
    "KYC_VERIFIED",
    "KYC_ACTION_REQUIRED",
    "KYC_REJECTED",
]
FarmerRegistrationState = Literal["NEW_IN_PROGRESS", "KYC_SUBMITTED"]
FarmerRegistrationNextStep = Literal["FARMER_DETAILS", "KYC", "HOME"]


class FarmerRegistrationDetails(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = PILOT_FARMER_STATE
    preferred_language: SupportedLanguage = "te"


class FarmerRegistrationStatus(BaseModel):
    registration_id: str
    registration_status: FarmerRegistrationState
    next_step: FarmerRegistrationNextStep
    full_name: str | None = None
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    preferred_language: SupportedLanguage

    @model_validator(mode="after")
    def validate_lifecycle(self):
        if self.registration_status == "KYC_SUBMITTED":
            if self.next_step != "HOME":
                raise ValueError("KYC_SUBMITTED registration must resume at HOME")
            return self
        expected = "KYC" if self.full_name else "FARMER_DETAILS"
        if self.next_step != expected:
            raise ValueError("Registration next_step does not match saved details")
        return self


class FarmerKYCSubmit(BaseModel):
    # The raw Aadhaar value is validated for this request only and is not persisted.
    aadhaar_number: str = Field(pattern=r"^\d{12}$")


class FarmerRegistrationComplete(BaseModel):
    farmer_id: str
    kyc_status: Literal["KYC_PENDING"]
    registration_status: Literal["KYC_SUBMITTED"]
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    token_type: Literal["bearer"] = "bearer"


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
    kyc_status: FarmerKYCStatus
    payout_status: str
    preferred_language: SupportedLanguage


class FarmerDashboardResponse(BaseModel):
    farmer_id: str
    kyc_status: FarmerKYCStatus
    transaction_enabled: bool
    live_listings: int = Field(ge=0)
    active_offers: int = Field(ge=0)
    settled_amount_paise: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_transaction_boundary(self):
        if self.transaction_enabled != (self.kyc_status == "KYC_VERIFIED"):
            raise ValueError("transaction_enabled must match Farmer KYC verification state")
        return self


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
