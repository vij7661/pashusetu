from pydantic import ValidationError
import pytest

from app.identity.schemas import (
    FarmerDashboardResponse,
    FarmerProfileResponse,
    FarmerRegistrationComplete,
)


def test_farmer_registration_completion_is_pending_kyc_account_conversion():
    response = FarmerRegistrationComplete(
        farmer_id="FARMER-1",
        kyc_status="KYC_PENDING",
        registration_status="KYC_SUBMITTED",
        access_token="access",
        refresh_token="refresh",
    )
    assert response.kyc_status == "KYC_PENDING"

    with pytest.raises(ValidationError):
        FarmerRegistrationComplete(
            farmer_id="FARMER-1",
            kyc_status="KYC_VERIFIED",
            registration_status="KYC_SUBMITTED",
            access_token="access",
            refresh_token="refresh",
        )


def test_farmer_profile_rejects_unknown_kyc_state_and_language():
    common = {
        "farmer_id": "FARMER-1",
        "full_name": "Ramesh Goud",
        "village": "Chityal",
        "mandal": "Chityal",
        "district": "Nalgonda",
        "state": "Telangana",
        "payout_status": "PENDING",
    }
    response = FarmerProfileResponse(
        **common,
        kyc_status="KYC_PENDING",
        preferred_language="te",
    )
    assert response.kyc_status == "KYC_PENDING"

    with pytest.raises(ValidationError):
        FarmerProfileResponse(
            **common,
            kyc_status="UNKNOWN_KYC_STATE",
            preferred_language="te",
        )
    with pytest.raises(ValidationError):
        FarmerProfileResponse(
            **common,
            kyc_status="KYC_PENDING",
            preferred_language="xx",
        )


def test_farmer_dashboard_requires_kyc_transaction_boundary_and_non_negative_counts():
    response = FarmerDashboardResponse(
        farmer_id="FARMER-1",
        kyc_status="KYC_VERIFIED",
        transaction_enabled=True,
        live_listings=0,
        active_offers=0,
        settled_amount_paise=0,
    )
    assert response.transaction_enabled is True

    with pytest.raises(ValidationError):
        FarmerDashboardResponse(
            farmer_id="FARMER-1",
            kyc_status="KYC_PENDING",
            transaction_enabled=True,
            live_listings=0,
            active_offers=0,
            settled_amount_paise=0,
        )
    with pytest.raises(ValidationError):
        FarmerDashboardResponse(
            farmer_id="FARMER-1",
            kyc_status="KYC_PENDING",
            transaction_enabled=False,
            live_listings=-1,
            active_offers=0,
            settled_amount_paise=0,
        )
