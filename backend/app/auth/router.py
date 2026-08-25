from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.auth.schemas import MeResponse, OTPRequest, OTPVerify, TokenPair
from app.auth.service import request_otp, tokens_for, verify_otp
from app.db.session import get_db
from app.identity.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED)
def otp_request(payload: OTPRequest, db: Session = Depends(get_db)):
    request_otp(db, payload.mobile_e164, payload.purpose)
    return {"status": "OTP_SENT"}


@router.post("/otp/verify", response_model=TokenPair)
def otp_verify(payload: OTPVerify, db: Session = Depends(get_db)):
    user, roles = verify_otp(db, payload.mobile_e164, payload.otp, payload.purpose)
    return tokens_for(user, roles)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(current_user)):
    return MeResponse(
        user_id=str(user.id),
        mobile_e164=user.mobile_e164,
        roles=[x.role for x in user.roles],
        preferred_language=user.preferred_language,
    )
