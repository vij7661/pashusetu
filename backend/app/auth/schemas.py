from pydantic import BaseModel, Field

OTP_LENGTH = 4


class OTPRequest(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    purpose: str = "LOGIN"


class OTPVerify(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    otp: str = Field(pattern=rf"^\d{{{OTP_LENGTH}}}$")
    purpose: str = "LOGIN"


class FarmerRegistrationSession(BaseModel):
    registration_id: str
    registration_token: str
    registration_status: str
    next_step: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    user_id: str
    mobile_e164: str
    roles: list[str]
    preferred_language: str
