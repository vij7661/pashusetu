from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SupportedLanguage = Literal["te", "hi", "en", "mr", "ta", "ml"]


class FarmerProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = "Telangana"
    latitude: float | None = None
    longitude: float | None = None
    preferred_language: SupportedLanguage = "te"
    kyc: "FarmerKycSubmission"
    payout: "FarmerPayoutSubmission"


class FarmerKycSubmission(BaseModel):
    aadhaar_number: str = Field(pattern=r"^\d{12}$")
    name_as_per_aadhaar: str = Field(min_length=2, max_length=120)
    consent: bool

    @field_validator("name_as_per_aadhaar")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("name is required")
        return value


class FarmerPayoutSubmission(BaseModel):
    method: Literal["UPI", "BANK"]
    upi_id: str | None = None
    account_holder_name: str | None = None
    account_number: str | None = None
    confirm_account_number: str | None = None
    ifsc: str | None = None

    @model_validator(mode="after")
    def validate_selected_method(self):
        if self.method == "UPI":
            import re

            if not self.upi_id or not re.fullmatch(r"[A-Za-z0-9._-]{2,}@[A-Za-z0-9.-]{2,}", self.upi_id.strip()):
                raise ValueError("invalid UPI ID")
        else:
            import re

            holder = (self.account_holder_name or "").strip()
            account = (self.account_number or "").strip()
            if len(holder) < 2 or not re.fullmatch(r"\d{6,18}", account):
                raise ValueError("invalid bank details")
            if account != (self.confirm_account_number or "").strip():
                raise ValueError("account numbers do not match")
            if not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", (self.ifsc or "").strip().upper()):
                raise ValueError("invalid IFSC")
        return self


class FarmerProfileResponse(BaseModel):
    farmer_id: str
    full_name: str
    village: str | None
    mandal: str | None
    district: str | None
    state: str | None
    kyc_status: str
    kyc_masked_id: str | None
    kyc_provider_reference: str | None
    payout_status: str
    payout_method: str | None
    payout_masked_reference: str | None
    preferred_language: str


class KycVerificationResponse(BaseModel):
    status: str
    masked_id: str
    provider_reference: str


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


FarmerProfileCreate.model_rebuild()
