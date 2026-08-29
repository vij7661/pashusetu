import pytest
from pydantic import ValidationError
from sqlalchemy import delete, select

from app.auth.schemas import OTPVerify
from app.auth.service import (
    FARMER_REGISTRATION_PURPOSE,
    _development_otp,
    request_otp,
    verify_farmer_registration_otp,
)
from app.db.session import SessionLocal
from app.identity.models import OTPChallenge, User, UserRole
from app.identity.profile_models import FarmerProfile, FarmerRegistration
from app.identity.schemas import FarmerRegistrationDetails
from app.identity.service import (
    complete_farmer_registration_kyc,
    save_farmer_registration_details,
)
from tests.fixtures.farmer_positive_v2 import FARMER_POSITIVE_V2


def test_otp_contract_is_exactly_four_numeric_digits():
    OTPVerify(mobile_e164="+919100000001", otp="1234", purpose="FARMER_REGISTRATION")

    for invalid in ("123", "12345", "12a4", "abcd", ""):
        with pytest.raises(ValidationError):
            OTPVerify(
                mobile_e164="+919100000001",
                otp=invalid,
                purpose="FARMER_REGISTRATION",
            )


def test_farmer_positive_v2_fixture_integrity():
    assert len(FARMER_POSITIVE_V2) == 40
    assert len({row["fixture_id"] for row in FARMER_POSITIVE_V2}) == 40
    assert len({row["registration_id"] for row in FARMER_POSITIVE_V2}) == 40
    assert len({row["mobile_e164"] for row in FARMER_POSITIVE_V2}) == 40
    assert len({row["dev_otp"] for row in FARMER_POSITIVE_V2}) == 40

    for row in FARMER_POSITIVE_V2:
        assert row["dev_otp"].isdigit()
        assert len(row["dev_otp"]) == 4
        assert _development_otp(row["mobile_e164"]) == row["dev_otp"]
        if row["registration_state"] in {"NEW_NOT_STARTED", "NEW_IN_PROGRESS"}:
            assert row["farmer_id"] is None
        else:
            assert row["farmer_id"] is not None

    counts = {}
    for row in FARMER_POSITIVE_V2:
        counts[row["registration_state"]] = counts.get(row["registration_state"], 0) + 1
    assert counts == {
        "NEW_NOT_STARTED": 16,
        "NEW_IN_PROGRESS": 8,
        "KYC_PENDING": 8,
        "KYC_VERIFIED": 8,
    }


def test_registration_resumes_and_farmer_id_is_created_only_after_kyc_submission():
    mobile = "+919199999901"
    db = SessionLocal()
    try:
        db.execute(delete(OTPChallenge).where(OTPChallenge.mobile_e164 == mobile))
        registration = db.scalar(
            select(FarmerRegistration).where(FarmerRegistration.mobile_e164 == mobile)
        )
        if registration is not None:
            if registration.user_id is not None:
                profile = db.scalar(
                    select(FarmerProfile).where(FarmerProfile.user_id == registration.user_id)
                )
                if profile is not None:
                    db.delete(profile)
                user = db.get(User, registration.user_id)
                db.delete(registration)
                if user is not None:
                    db.execute(delete(UserRole).where(UserRole.user_id == user.id))
                    db.delete(user)
            else:
                db.delete(registration)
        db.commit()

        request_otp(db, mobile, FARMER_REGISTRATION_PURPOSE)
        registration, _, next_step = verify_farmer_registration_otp(
            db, mobile, _development_otp(mobile)
        )

        assert next_step == "FARMER_DETAILS"
        assert registration.status == "NEW_IN_PROGRESS"
        assert registration.user_id is None
        assert db.scalar(select(User).where(User.mobile_e164 == mobile)) is None

        registration_id = registration.id
        save_farmer_registration_details(
            db,
            registration,
            FarmerRegistrationDetails(
                full_name="Lifecycle Test Farmer",
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
        assert resumed.full_name == "Lifecycle Test Farmer"
        assert resumed.user_id is None
        assert next_step == "KYC"
        assert db.scalar(select(User).where(User.mobile_e164 == mobile)) is None

        profile, _ = complete_farmer_registration_kyc(
            db, resumed, "123412341234"
        )
        db.refresh(resumed)

        user = db.scalar(select(User).where(User.mobile_e164 == mobile))
        assert user is not None
        assert resumed.user_id == user.id
        assert resumed.status == "KYC_SUBMITTED"
        assert profile.user_id == user.id
        assert profile.farmer_code.startswith("PS-F-")
        assert profile.kyc_status == "KYC_PENDING"
        assert resumed.kyc_reference == profile.kyc_reference
        assert not hasattr(resumed, "aadhaar_number")
        assert not hasattr(profile, "aadhaar_number")
    finally:
        db.rollback()
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
        db.commit()
        db.close()
