import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.service import DEV_OTP
from app.core.config import get_settings
from app.db.qa_fixtures import QA_USERS_BY_ID
from app.db.session import SessionLocal
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.main import app

FIXTURE = QA_USERS_BY_ID["FARMER_TE_001"]


@pytest.fixture(autouse=True)
def role_only_farmer_fixture():
    settings = get_settings()
    if settings.app_env != "qa" or not settings.database_isolated_for_qa:
        pytest.skip("requires explicitly isolated QA database")
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.mobile_e164 == FIXTURE.mobile_e164))
        assert user is not None
        db.execute(delete(FarmerProfile).where(FarmerProfile.user_id == user.id))
        db.commit()
    yield
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.mobile_e164 == FIXTURE.mobile_e164))
        db.execute(delete(FarmerProfile).where(FarmerProfile.user_id == user.id))
        db.commit()


def test_canonical_role_only_farmer_can_complete_profile_registration():
    client = TestClient(app)
    auth_payload = {"mobile_e164": FIXTURE.mobile_e164, "purpose": "LOGIN"}
    assert client.post("/api/v1/auth/otp/request", json=auth_payload).status_code == 202
    verified = client.post(
        "/api/v1/auth/otp/verify",
        json={**auth_payload, "otp": DEV_OTP},
    )
    assert verified.status_code == 200

    headers = {"Authorization": f"Bearer {verified.json()['access_token']}"}
    ui_payload = {
        "full_name": "Synthetic Telugu Farmer",
        "village": "QA Village",
        "mandal": "QA Mandal",
        "district": "QA District",
        "state": "Telangana",
        "preferred_language": "te",
        "kyc": {
            "aadhaar_number": "999971658847",
            "name_as_per_aadhaar": "Kumar Agarwal",
            "consent": True,
        },
        "payout": {
            "method": "BANK",
            "account_holder_name": "Kumar Agarwal",
            "account_number": "123456789012",
            "confirm_account_number": "123456789012",
            "ifsc": "HDFC0001234",
        },
    }
    response = client.post("/api/v1/identity/farmers", headers=headers, json=ui_payload)
    assert response.status_code == 201
    assert response.json()["preferred_language"] == "te"
    body = response.json()
    assert body["kyc_status"] == "QA_VERIFIED"
    assert body["kyc_masked_id"] == "XXXXXXXX8847"
    assert body["payout_status"] == "QA_CONFIGURED"
    assert body["payout_masked_reference"] == "XXXXXXXX9012"
    assert "999971658847" not in response.text
    assert "123456789012" not in response.text
    duplicate = client.post("/api/v1/identity/farmers", headers=headers, json=ui_payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "FARMER_PROFILE_EXISTS"
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.mobile_e164 == FIXTURE.mobile_e164))
        profiles = db.scalars(select(FarmerProfile).where(FarmerProfile.user_id == user.id)).all()
        assert len(profiles) == 1


def test_existing_farmer_profile_conflict_remains_protected():
    existing = QA_USERS_BY_ID["FARMER_EN_001"]
    client = TestClient(app)
    auth_payload = {"mobile_e164": existing.mobile_e164, "purpose": "LOGIN"}
    assert client.post("/api/v1/auth/otp/request", json=auth_payload).status_code == 202
    verified = client.post("/api/v1/auth/otp/verify", json={**auth_payload, "otp": DEV_OTP})
    response = client.post(
        "/api/v1/identity/farmers",
        headers={"Authorization": f"Bearer {verified.json()['access_token']}"},
        json={
            "full_name": "Existing Farmer",
            "preferred_language": "en",
            "kyc": {
                "aadhaar_number": "999941057058",
                "name_as_per_aadhaar": "Shivshankar Choudhury",
                "consent": True,
            },
            "payout": {"method": "UPI", "upi_id": "farmer.en@pashusetuqa"},
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == "FARMER_PROFILE_EXISTS"


def test_unseeded_qa_kyc_fails_closed_without_profile_side_effect():
    client = TestClient(app)
    auth_payload = {"mobile_e164": FIXTURE.mobile_e164, "purpose": "LOGIN"}
    assert client.post("/api/v1/auth/otp/request", json=auth_payload).status_code == 202
    verified = client.post("/api/v1/auth/otp/verify", json={**auth_payload, "otp": DEV_OTP})
    token = verified.json()["access_token"]
    response = client.post(
        "/api/v1/identity/farmers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Synthetic Telugu Farmer",
            "preferred_language": "te",
            "kyc": {
                "aadhaar_number": "999999999999",
                "name_as_per_aadhaar": "Unknown Tester",
                "consent": True,
            },
            "payout": {"method": "UPI", "upi_id": "farmer.qa@pashusetuqa"},
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "QA_KYC_NOT_FOUND"
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.mobile_e164 == FIXTURE.mobile_e164))
        assert db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id)) is None
