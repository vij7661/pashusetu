from typing import Literal

from pydantic import BaseModel, Field

OTP_LENGTH = 4
SupportedLanguage = Literal["te", "hi", "en", "mr", "ta", "ml"]


class OTPRequest(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    purpose: str = "LOGIN"


class OTPVerify(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    otp: str = Field(pattern=rf"^\d{{{OTP_LENGTH}}}$")
    purpose: str = "LOGIN"


class FarmerRegistrationSession(BaseModel):
    registration_id: str = Field(min_length=1)
    registration_token: str = Field(min_length=1)
    registration_status: Literal["NEW_IN_PROGRESS"]
    next_step: Literal["FARMER_DETAILS", "KYC"]


class TokenPair(BaseModel):
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    token_type: Literal["bearer"] = "bearer"


class MeResponse(BaseModel):
    user_id: str = Field(min_length=1)
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    roles: list[str] = Field(min_length=1)
    preferred_language: SupportedLanguage
