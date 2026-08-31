import pytest
from pydantic import ValidationError

from app.auth.schemas import FarmerRegistrationSession, MeResponse, TokenPair


def test_farmer_registration_session_is_temporary_only():
    session = FarmerRegistrationSession(
        registration_id="REG-1",
        registration_token="token",
        registration_status="NEW_IN_PROGRESS",
        next_step="FARMER_DETAILS",
    )
    assert session.next_step == "FARMER_DETAILS"

    with pytest.raises(ValidationError):
        FarmerRegistrationSession(
            registration_id="REG-1",
            registration_token="token",
            registration_status="KYC_SUBMITTED",
            next_step="HOME",
        )


def test_auth_token_pair_requires_bearer_and_non_empty_tokens():
    TokenPair(access_token="access", refresh_token="refresh", token_type="bearer")

    with pytest.raises(ValidationError):
        TokenPair(access_token="", refresh_token="refresh", token_type="bearer")
    with pytest.raises(ValidationError):
        TokenPair(access_token="access", refresh_token="refresh", token_type="basic")


def test_me_response_requires_supported_language_and_identity_shape():
    MeResponse(
        user_id="user-1",
        mobile_e164="+919100000001",
        roles=["FARMER"],
        preferred_language="te",
    )

    with pytest.raises(ValidationError):
        MeResponse(
            user_id="user-1",
            mobile_e164="9100000001",
            roles=["FARMER"],
            preferred_language="te",
        )
    with pytest.raises(ValidationError):
        MeResponse(
            user_id="user-1",
            mobile_e164="+919100000001",
            roles=["FARMER"],
            preferred_language="xx",
        )
