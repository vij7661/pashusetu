from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    purpose: str = "LOGIN"


class OTPVerify(BaseModel):
    mobile_e164: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    otp: str = Field(min_length=4, max_length=8)
    purpose: str = "LOGIN"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    user_id: str
    mobile_e164: str
    roles: list[str]
    preferred_language: str
