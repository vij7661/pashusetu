"""Headless verification of Farmer lifecycle QA data and routing preconditions."""

from pathlib import Path
from runpy import run_path

from sqlalchemy import delete, select

from app.auth.service import (
    FARMER_LOGIN_PURPOSE,
    FARMER_REGISTRATION_PURPOSE,
    _development_otp,
    request_otp,
    verify_farmer_registration_otp,
    verify_otp,
)
from app.db.session import SessionLocal
from app.identity.models import OTPChallenge, User
from app.identity.profile_models import FarmerProfile, FarmerRegistration

_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "farmer_lifecycle_v3.py"
)
FARMER_LIFECYCLE_QA = run_path(str(_FIXTURE_PATH))["FARMER_LIFECYCLE_QA"]


def _row(state: str) -> dict:
    return next(row for row in FARMER_LIFECYCLE_QA if row["lifecycle_state"] == state)


def verify_lifecycle_qa() -> None:
    db = SessionLocal()
    touched_mobiles: set[str] = set()
    try:
        fresh = _row("NEW_NOT_STARTED")
        assert db.scalar(
            select(User).where(User.mobile_e164 == fresh["mobile_e164"])
        ) is None
        assert db.scalar(
            select(FarmerRegistration).where(
                FarmerRegistration.mobile_e164 == fresh["mobile_e164"]
            )
        ) is None

        started = _row("REGISTRATION_STARTED")
        started_registration = db.scalar(
            select(FarmerRegistration).where(
                FarmerRegistration.mobile_e164 == started["mobile_e164"]
            )
        )
        assert started_registration is not None
        assert started_registration.user_id is None
        assert started_registration.full_name is None
        request_otp(db, started["mobile_e164"], FARMER_REGISTRATION_PURPOSE)
        touched_mobiles.add(started["mobile_e164"])
        resumed, _, next_step = verify_farmer_registration_otp(
            db, started["mobile_e164"], _development_otp(started["mobile_e164"])
        )
        assert resumed.id == started_registration.id
        assert next_step == "FARMER_DETAILS"

        details = _row("DETAILS_COMPLETED")
        details_registration = db.scalar(
            select(FarmerRegistration).where(
                FarmerRegistration.mobile_e164 == details["mobile_e164"]
            )
        )
        assert details_registration is not None
        assert details_registration.user_id is None
        assert details_registration.full_name
        request_otp(db, details["mobile_e164"], FARMER_REGISTRATION_PURPOSE)
        touched_mobiles.add(details["mobile_e164"])
        resumed, _, next_step = verify_farmer_registration_otp(
            db, details["mobile_e164"], _development_otp(details["mobile_e164"])
        )
        assert resumed.id == details_registration.id
        assert next_step == "KYC"

        for state in ("KYC_PENDING", "KYC_VERIFIED"):
            fixture = _row(state)
            user = db.scalar(select(User).where(User.mobile_e164 == fixture["mobile_e164"]))
            assert user is not None
            profile = db.scalar(
                select(FarmerProfile).where(FarmerProfile.user_id == user.id)
            )
            assert profile is not None
            assert profile.kyc_status == fixture["kyc_status"]
            request_otp(db, fixture["mobile_e164"], FARMER_LOGIN_PURPOSE)
            touched_mobiles.add(fixture["mobile_e164"])
            logged_in_user, roles = verify_otp(
                db,
                fixture["mobile_e164"],
                _development_otp(fixture["mobile_e164"]),
                FARMER_LOGIN_PURPOSE,
            )
            assert logged_in_user.id == user.id
            assert "FARMER" in roles

        print("Farmer lifecycle QA headless verification passed")
        print("NEW_NOT_STARTED -> no registration/account")
        print("REGISTRATION_STARTED -> FARMER_DETAILS")
        print("DETAILS_COMPLETED -> KYC")
        print("KYC_PENDING/KYC_VERIFIED -> existing Farmer login")
    finally:
        db.rollback()
        if touched_mobiles:
            db.execute(delete(OTPChallenge).where(OTPChallenge.mobile_e164.in_(touched_mobiles)))
            db.commit()
        db.close()


if __name__ == "__main__":
    verify_lifecycle_qa()
