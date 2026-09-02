import pytest
from sqlalchemy import delete, select

from app.auth.service import (
    FARMER_LOGIN_PURPOSE,
    FARMER_REGISTRATION_PURPOSE,
    _development_otp,
    request_otp,
    verify_farmer_registration_otp,
    verify_otp,
)
from app.core.errors import AppError
from app.db.session import SessionLocal
from app.identity.models import OTPChallenge, User, UserRole
from app.identity.profile_models import FarmerProfile, FarmerRegistration
from app.identity.schemas import FarmerRegistrationDetails
from app.identity.service import (
    complete_farmer_registration_kyc,
    save_farmer_registration_details,
)


def _reset_identity(db, mobile: str) -> None:
    db.execute(delete(OTPChallenge).where(OTPChallenge.mobile_e164 == mobile))
    registration = db.scalar(
        select(FarmerRegistration).where(FarmerRegistration.mobile_e164 == mobile)
    )
    if registration is not None:
        user_id = registration.user_id
        if user_id is not None:
            db.execute(delete(FarmerProfile).where(FarmerProfile.user_id == user_id))
            db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        db.delete(registration)
        if user_id is not None:
            db.execute(delete(User).where(User.id == user_id))
    else:
        user = db.scalar(select(User).where(User.mobile_e164 == mobile))
        if user is not None:
            db.execute(delete(FarmerProfile).where(FarmerProfile.user_id == user.id))
            db.execute(delete(UserRole).where(UserRole.user_id == user.id))
            db.delete(user)
    db.commit()


def test_farmer_identity_fixture_follows_authoritative_lifecycle():
    mobile = "+919199999902"
    db = SessionLocal()
    try:
        _reset_identity(db, mobile)

        # A fresh identity remains a registration identity after OTP verification.
        # OTP verification alone does not create an existing Farmer account.
        request_otp(db, mobile, FARMER_REGISTRATION_PURPOSE)
        registration, _, next_step = verify_farmer_registration_otp(
            db, mobile, _development_otp(mobile)
        )
        assert next_step == "FARMER_DETAILS"
        assert registration.user_id is None
        assert db.scalar(select(User).where(User.mobile_e164 == mobile)) is None

        # Until account creation, the same identity resumes the same registration
        # rather than being reset and treated as a brand-new fixture.
        registration_id = registration.id
        save_farmer_registration_details(
            db,
            registration,
            FarmerRegistrationDetails(
                full_name="Lifecycle Guard Farmer",
                village="Chityal",
                mandal="Chityal",
                district="Nalgonda",
                state="Telangana",
                preferred_language="te",
            ),
        )
        request_otp(db, mobile, FARMER_REGISTRATION_PURPOSE)
        resumed, _, next_step = verify_farmer_registration_otp(
            db, mobile, _development_otp(mobile)
        )
        assert resumed.id == registration_id
        assert next_step == "KYC"

        # KYC submission converts the registration into an authoritative Farmer
        # account. From this point the identity is existing and must not be reused
        # by a NEW-user fixture unless the environment is explicitly reset/reseeded.
        profile, _ = complete_farmer_registration_kyc(db, resumed, "123412341234")
        db.refresh(resumed)
        user = db.scalar(select(User).where(User.mobile_e164 == mobile))
        assert user is not None
        assert resumed.user_id == user.id
        assert profile.user_id == user.id

        request_otp(db, mobile, FARMER_REGISTRATION_PURPOSE)
        with pytest.raises(AppError) as exc_info:
            verify_farmer_registration_otp(db, mobile, _development_otp(mobile))
        assert exc_info.value.code == "FARMER_ALREADY_REGISTERED"

        # The same lifecycle identity is now valid through the existing Farmer
        # login path, proving the state transition is respected by the test data.
        request_otp(db, mobile, FARMER_LOGIN_PURPOSE)
        logged_in_user, roles = verify_otp(
            db,
            mobile,
            _development_otp(mobile),
            FARMER_LOGIN_PURPOSE,
        )
        assert logged_in_user.id == user.id
        assert "FARMER" in roles
    finally:
        db.rollback()
        _reset_identity(db, mobile)
        db.close()
