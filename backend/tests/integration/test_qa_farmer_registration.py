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

    response = client.post(
        "/api/v1/identity/farmers",
        headers={"Authorization": f"Bearer {verified.json()['access_token']}"},
        json={
            "full_name": "Synthetic Telugu Farmer",
            "village": "QA Village",
            "mandal": "QA Mandal",
            "district": "QA District",
            "state": "Telangana",
            "preferred_language": "te",
        },
    )
    assert response.status_code == 201
    assert response.json()["preferred_language"] == "te"
    assert response.json()["kyc_status"] == "PENDING"
