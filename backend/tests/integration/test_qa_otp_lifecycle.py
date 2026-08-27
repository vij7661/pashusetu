from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.auth.service import DEV_OTP, _hash_otp
from app.core.config import get_settings
from app.db.qa_fixtures import QA_USERS_BY_ID
from app.db.session import SessionLocal
from app.identity.models import OTPChallenge, User
from app.main import app

MOBILE = QA_USERS_BY_ID["FARMER_EN_001"].mobile_e164


@pytest.fixture(autouse=True)
def isolated_seeded_qa_identity():
    settings = get_settings()
    if settings.app_env != "qa" or not settings.database_isolated_for_qa:
        pytest.skip("requires explicitly isolated QA database")
    with SessionLocal() as db:
        assert db.scalar(select(User).where(User.mobile_e164 == MOBILE)) is not None
        db.execute(delete(OTPChallenge).where(OTPChallenge.mobile_e164 == MOBILE))
        db.commit()
    yield
    with SessionLocal() as db:
        db.execute(delete(OTPChallenge).where(OTPChallenge.mobile_e164 == MOBILE))
        db.commit()


def test_seeded_request_resend_wrong_success_and_single_use():
    client = TestClient(app)
    payload = {"mobile_e164": MOBILE, "purpose": "LOGIN"}

    assert client.post("/api/v1/auth/otp/request", json=payload).status_code == 202
    assert client.post("/api/v1/auth/otp/request", json=payload).status_code == 202

    with SessionLocal() as db:
        total = db.scalar(
            select(func.count()).select_from(OTPChallenge).where(
                OTPChallenge.mobile_e164 == MOBILE
            )
        )
        active = db.scalar(
            select(func.count()).select_from(OTPChallenge).where(
                OTPChallenge.mobile_e164 == MOBILE,
                OTPChallenge.consumed.is_(False),
            )
        )
    assert total == 2
    assert active == 1

    wrong = client.post(
        "/api/v1/auth/otp/verify",
        json={**payload, "otp": "0000"},
    )
    assert wrong.status_code == 400
    assert wrong.json()["code"] == "OTP_INVALID"

    success = client.post(
        "/api/v1/auth/otp/verify",
        json={**payload, "otp": DEV_OTP},
    )
    assert success.status_code == 200
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {success.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["roles"] == ["FARMER"]

    reuse = client.post(
        "/api/v1/auth/otp/verify",
        json={**payload, "otp": DEV_OTP},
    )
    assert reuse.status_code == 400
    assert reuse.json()["code"] == "OTP_NOT_FOUND"


def test_expired_qa_otp_is_rejected():
    with SessionLocal() as db:
        db.add(
            OTPChallenge(
                mobile_e164=MOBILE,
                purpose="LOGIN",
                otp_hash=_hash_otp(DEV_OTP),
                expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
            )
        )
        db.commit()

    response = TestClient(app).post(
        "/api/v1/auth/otp/verify",
        json={"mobile_e164": MOBILE, "purpose": "LOGIN", "otp": DEV_OTP},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "OTP_EXPIRED"


def test_unseeded_valid_mobile_has_zero_otp_side_effects():
    unseeded_mobile = "+919999999999"
    response = TestClient(app).post(
        "/api/v1/auth/otp/request",
        json={"mobile_e164": unseeded_mobile, "purpose": "LOGIN"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "QA_TEST_USER_NOT_FOUND"
    with SessionLocal() as db:
        count = db.scalar(
            select(func.count()).select_from(OTPChallenge).where(
                OTPChallenge.mobile_e164 == unseeded_mobile
            )
        )
    assert count == 0
