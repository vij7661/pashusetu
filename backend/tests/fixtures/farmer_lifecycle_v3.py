"""Authoritative Farmer lifecycle fixtures for automated and manual QA.

Each identity represents exactly one starting lifecycle state. State-changing tests must
not reuse an identity as though it were still in an earlier state; use a disposable
identity or explicitly reset/reseed the QA database.
"""

from app.auth.service import _development_otp

FARMER_LIFECYCLE_QA = [
    {
        "fixture_id": "FLC-001",
        "mobile_e164": "+919100000001",
        "dev_otp": _development_otp("+919100000001"),
        "lifecycle_state": "NEW_NOT_STARTED",
        "registration_exists": False,
        "farmer_account_exists": False,
        "details_completed": False,
        "kyc_status": "NOT_SUBMITTED",
        "expected_registration_next_step": "FARMER_DETAILS",
        "reuse_policy": "CONSUMABLE_RESET_REQUIRED",
    },
    {
        "fixture_id": "FLC-009",
        "mobile_e164": "+919100000009",
        "dev_otp": _development_otp("+919100000009"),
        "lifecycle_state": "REGISTRATION_STARTED",
        "registration_exists": True,
        "farmer_account_exists": False,
        "details_completed": False,
        "kyc_status": "NOT_SUBMITTED",
        "expected_registration_next_step": "FARMER_DETAILS",
        "reuse_policy": "STABLE_UNTIL_MUTATED",
    },
    {
        "fixture_id": "FLC-017",
        "mobile_e164": "+919100000017",
        "dev_otp": _development_otp("+919100000017"),
        "lifecycle_state": "DETAILS_COMPLETED",
        "registration_exists": True,
        "farmer_account_exists": False,
        "details_completed": True,
        "kyc_status": "NOT_SUBMITTED",
        "expected_registration_next_step": "KYC",
        "reuse_policy": "STABLE_UNTIL_MUTATED",
    },
    {
        "fixture_id": "FLC-025",
        "mobile_e164": "+919100000025",
        "dev_otp": _development_otp("+919100000025"),
        "lifecycle_state": "KYC_PENDING",
        "registration_exists": True,
        "farmer_account_exists": True,
        "details_completed": True,
        "kyc_status": "KYC_PENDING",
        "expected_registration_next_step": None,
        "reuse_policy": "STABLE_READ_ONLY",
    },
    {
        "fixture_id": "FLC-033",
        "mobile_e164": "+919100000033",
        "dev_otp": _development_otp("+919100000033"),
        "lifecycle_state": "KYC_VERIFIED",
        "registration_exists": True,
        "farmer_account_exists": True,
        "details_completed": True,
        "kyc_status": "KYC_VERIFIED",
        "expected_registration_next_step": None,
        "reuse_policy": "STABLE_READ_ONLY",
    },
]
