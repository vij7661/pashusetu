"""Verify the seeded Farmer weighment-review contract end to end in test CI."""

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.main import app
from app.weighment.models import (
    FarmerWeighmentAcknowledgement,
    WeighmentReceipt,
    WeighmentSession,
)

OWNER_FARMER_CODE = "F-FV2-033"
OTHER_FARMER_CODE = "F-FV2-025"
WEIGHMENT_CODE = "WG-QA-ACK-001"


def _token(db, farmer_code: str) -> str:
    farmer = db.scalar(
        select(FarmerProfile).where(FarmerProfile.farmer_code == farmer_code)
    )
    if farmer is None:
        raise RuntimeError(f"Missing QA Farmer {farmer_code}")
    user = db.get(User, farmer.user_id)
    return create_access_token(str(user.id), [role.role for role in user.roles])


def verify() -> None:
    db = SessionLocal()
    client = TestClient(app)
    try:
        owner_token = _token(db, OWNER_FARMER_CODE)
        other_token = _token(db, OTHER_FARMER_CODE)
        headers = {"Authorization": f"Bearer {owner_token}"}

        review = client.get(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/farmer-review",
            headers=headers,
        )
        assert review.status_code == 200, review.text
        payload = review.json()
        assert payload["weighment_id"] == WEIGHMENT_CODE
        assert payload["target_id"] == "GOAT-QA-ACK"
        assert payload["net_kg"] == "47.250"
        assert payload["verification_evidence_present"] is True
        assert payload["status"] == "FARMER_REVIEW"

        forbidden = client.get(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/farmer-review",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert forbidden.status_code == 403, forbidden.text
        assert forbidden.json()["code"] == "WEIGHMENT_NOT_OWNED"

        reject = client.post(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/acknowledge",
            headers=headers,
            json={"acknowledged": False, "method": "APP_CONFIRMATION"},
        )
        assert reject.status_code == 200, reject.text
        assert reject.json()["status"] == "REJECTED_BY_FARMER"

        session = db.scalar(
            select(WeighmentSession).where(
                WeighmentSession.weighment_code == WEIGHMENT_CODE
            )
        )
        db.expire_all()
        db.refresh(session)
        decision = db.scalar(
            select(FarmerWeighmentAcknowledgement).where(
                FarmerWeighmentAcknowledgement.weighment_session_id == session.id
            )
        )
        assert decision is not None and decision.acknowledged is False
        assert db.scalar(
            select(WeighmentReceipt).where(
                WeighmentReceipt.weighment_session_id == session.id
            )
        ) is None

        no_receipt = client.post(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/receipt",
            headers=headers,
        )
        assert no_receipt.status_code == 409, no_receipt.text
        assert no_receipt.json()["code"] == "ACK_REQUIRED"

        # Reset only this controlled test decision to verify the independent accept path.
        db.execute(
            delete(FarmerWeighmentAcknowledgement).where(
                FarmerWeighmentAcknowledgement.weighment_session_id == session.id
            )
        )
        session.status = "FARMER_REVIEW"
        db.commit()

        accept = client.post(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/acknowledge",
            headers=headers,
            json={"acknowledged": True, "method": "APP_CONFIRMATION"},
        )
        assert accept.status_code == 200, accept.text
        assert accept.json()["status"] == "ACKNOWLEDGED"

        receipt = client.post(
            f"/api/v1/weighment/sessions/{WEIGHMENT_CODE}/receipt",
            headers=headers,
        )
        assert receipt.status_code == 200, receipt.text
        assert receipt.json()["receipt_code"].startswith("RCPT-")

        db.expire_all()
        db.refresh(session)
        assert session.status == "VERIFIED"
        print("Farmer weighment-review QA contract verified")
    finally:
        db.close()


if __name__ == "__main__":
    verify()
