from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth import service
from app.auth.schemas import OTPRequest
from app.core.config import Settings
from app.core.errors import AppError
from app.db.session import get_db
from app.main import app


class FakeDB:
    def __init__(self, user=None):
        self.user = user
        self.added = []
        self.commits = 0

    def scalar(self, _query):
        return self.user

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.commits += 1


def test_backend_rejects_invalid_indian_mobile_before_otp_state():
    with pytest.raises(ValidationError):
        OTPRequest(mobile_e164="+91987654321", purpose="LOGIN")
    with pytest.raises(ValidationError):
        OTPRequest(mobile_e164="+9198765432100", purpose="LOGIN")

    app.dependency_overrides[get_db] = lambda: FakeDB()
    try:
        response = TestClient(app).post(
            "/api/v1/auth/otp/request",
            json={"mobile_e164": "+91987654321", "purpose": "LOGIN"},
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_unseeded_valid_qa_number_creates_no_challenge(monkeypatch):
    db = FakeDB(user=None)
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(otp_test_mode=True, otp_ttl_seconds=300),
    )

    with pytest.raises(AppError) as exc:
        service.request_otp(db, "+919999999999", "LOGIN")

    assert exc.value.code == "QA_TEST_USER_NOT_FOUND"
    assert db.added == []
    assert db.commits == 0


def test_seeded_qa_number_can_create_test_challenge(monkeypatch):
    sent = []
    db = FakeDB(user=SimpleNamespace(mobile_e164="+919876543210"))
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(otp_test_mode=True, otp_ttl_seconds=300),
    )
    monkeypatch.setattr(
        service.DevelopmentOTPProvider,
        "send",
        lambda _provider, mobile, otp: sent.append((mobile, otp)),
    )

    service.request_otp(db, "+919876543210", "LOGIN")

    assert len(db.added) == 1
    assert db.commits == 1
    assert sent == [("+919876543210", service.DEV_OTP)]


def test_test_otp_mode_is_disabled_by_default(monkeypatch):
    db = FakeDB(user=object())
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(otp_test_mode=False),
    )

    with pytest.raises(AppError) as exc:
        service.request_otp(db, "+919876543210", "LOGIN")

    assert exc.value.code == "OTP_PROVIDER_UNAVAILABLE"
    assert db.added == []


@pytest.mark.parametrize(
    ("app_env", "isolated"),
    [("production", True), ("pilot", True), ("qa", False), ("local", False)],
)
def test_test_otp_mode_fails_closed_outside_isolated_qa(app_env, isolated):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env=app_env,
            otp_test_mode=True,
            database_isolated_for_qa=isolated,
        )


def test_test_otp_mode_accepts_explicit_isolated_qa_configuration():
    settings = Settings(
        _env_file=None,
        app_env="qa",
        otp_test_mode=True,
        database_isolated_for_qa=True,
    )
    assert settings.otp_test_mode is True
