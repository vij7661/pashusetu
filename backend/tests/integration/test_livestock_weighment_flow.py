from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.identity.models import User, UserRole
from app.identity.profile_models import FarmerProfile
from app.livestock.models import Goat
from app.main import app
from app.weighment.models import (
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
)


def _headers(user: User, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id), [role])}"}


def test_livestock_and_weighment_trust_flow(postgres_available):
    connection = postgres_available.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    suffix = uuid4().hex[:8]
    try:
        farmer_user = User(mobile_e164=f"+9190{suffix[:8]}", preferred_language="te")
        other_farmer = User(mobile_e164=f"+9180{suffix[:8]}", preferred_language="en")
        operator_user = User(mobile_e164=f"+9170{suffix[:8]}", preferred_language="en")
        db.add_all([farmer_user, other_farmer, operator_user])
        db.flush()
        db.add_all(
            [
                UserRole(user_id=farmer_user.id, role="FARMER"),
                UserRole(user_id=other_farmer.id, role="FARMER"),
                UserRole(user_id=operator_user.id, role="OPERATOR"),
            ]
        )
        centre = MandalCentre(centre_code=f"C-{suffix}", name="Synthetic Test Centre")
        db.add(centre)
        db.flush()
        farmer = FarmerProfile(
            user_id=farmer_user.id, farmer_code=f"F-{suffix}", full_name="Synthetic Farmer"
        )
        other = FarmerProfile(
            user_id=other_farmer.id, farmer_code=f"O-{suffix}", full_name="Other Farmer"
        )
        operator = OperatorProfile(
            user_id=operator_user.id,
            operator_code=f"OP-{suffix}",
            full_name="Synthetic Operator",
            centre_id=centre.id,
        )
        scale = ScaleDevice(
            scale_code=f"S-{suffix}", centre_id=centre.id, calibration_status="VALID", active=True
        )
        db.add_all([farmer, other, operator, scale])
        db.commit()

        def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        client = TestClient(app)
        farmer_headers = _headers(farmer_user, "FARMER")
        other_headers = _headers(other_farmer, "FARMER")
        operator_headers = _headers(operator_user, "OPERATOR")

        goat = client.post(
            "/api/v1/livestock/goats",
            json={"breed": "Deccani", "sex": "FEMALE", "age_months": 18},
            headers=farmer_headers,
        )
        assert goat.status_code == 201
        goat_code = goat.json()["goat_id"]
        retrieved = client.get(f"/api/v1/livestock/goats/{goat_code}", headers=farmer_headers)
        assert retrieved.status_code == 200
        assert retrieved.json()["goat_id"] == goat_code
        assert (
            db.scalar(
                select(func.count(Goat.id)).where(
                    Goat.goat_code == goat_code,
                    Goat.farmer_profile_id == farmer.id,
                )
            )
            == 1
        )
        assert (
            client.get(f"/api/v1/livestock/goats/{goat_code}", headers=other_headers).status_code
            == 404
        )
        lot = client.post(
            "/api/v1/livestock/lots",
            json={"declared_quantity": 2, "goat_ids": [goat_code]},
            headers=farmer_headers,
        )
        assert lot.status_code == 201
        assert lot.json()["linked_goat_ids"] == [goat_code]

        started = client.post(
            "/api/v1/weighment/sessions",
            json={"target_type": "GOAT", "target_id": goat_code, "scale_code": scale.scale_code},
            headers=operator_headers,
        )
        assert started.status_code == 201
        weighment_code = started.json()["weighment_id"]
        unstable = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/readings",
            json={"gross_kg": 51.25, "tare_kg": 1.25, "stable": False},
            headers=operator_headers,
        )
        assert unstable.status_code == 201
        denied = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/lock",
            json={"reading_id": unstable.json()["reading_id"]},
            headers=operator_headers,
        )
        assert denied.status_code == 409
        stable = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/readings",
            json={"gross_kg": 51.5, "tare_kg": 1.5, "stable": True},
            headers=operator_headers,
        )
        locked = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/lock",
            json={"reading_id": stable.json()["reading_id"]},
            headers=operator_headers,
        )
        assert locked.status_code == 200 and locked.json()["net_kg"] == "50.000"
        evidence = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/verification-evidence",
            json={"file_name": "synthetic.mp4", "mime_type": "video/mp4"},
            headers=operator_headers,
        )
        attached = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/verification-video",
            json={"video_evidence_id": evidence.json()["evidence_id"]},
            headers=operator_headers,
        )
        assert attached.status_code == 200 and attached.json()["status"] == "FARMER_REVIEW"
        assert (
            client.post(
                f"/api/v1/weighment/sessions/{weighment_code}/acknowledge",
                json={"acknowledged": True},
                headers=other_headers,
            ).status_code
            == 403
        )
        rejected = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/acknowledge",
            json={"acknowledged": False},
            headers=farmer_headers,
        )
        assert rejected.status_code == 200 and rejected.json()["status"] == "REJECTED_BY_FARMER"
        reweigh = client.post(
            f"/api/v1/weighment/sessions/{weighment_code}/reweigh",
            json={"scale_code": scale.scale_code},
            headers=operator_headers,
        )
        assert reweigh.status_code == 201
        original = db.query(WeighmentSession).filter_by(weighment_code=weighment_code).one()
        replacement = (
            db.query(WeighmentSession)
            .filter_by(weighment_code=reweigh.json()["weighment_id"])
            .one()
        )
        assert replacement.reweigh_of_id == original.id
        assert (
            db.query(WeightReading)
            .filter_by(weighment_session_id=original.id, locked=True)
            .one()
            .net_kg
            == 50
        )

        replacement_code = reweigh.json()["weighment_id"]
        second = client.post(
            f"/api/v1/weighment/sessions/{replacement_code}/readings",
            json={"gross_kg": 51.4, "tare_kg": 1.4, "stable": True},
            headers=operator_headers,
        )
        assert (
            client.post(
                f"/api/v1/weighment/sessions/{replacement_code}/lock",
                json={"reading_id": second.json()["reading_id"]},
                headers=operator_headers,
            ).status_code
            == 200
        )
        second_evidence = client.post(
            f"/api/v1/weighment/sessions/{replacement_code}/verification-evidence",
            json={"file_name": "synthetic-reweigh.mp4", "mime_type": "video/mp4"},
            headers=operator_headers,
        )
        assert (
            client.post(
                f"/api/v1/weighment/sessions/{replacement_code}/verification-video",
                json={"video_evidence_id": second_evidence.json()["evidence_id"]},
                headers=operator_headers,
            ).status_code
            == 200
        )
        accepted = client.post(
            f"/api/v1/weighment/sessions/{replacement_code}/acknowledge",
            json={"acknowledged": True},
            headers=farmer_headers,
        )
        assert accepted.status_code == 200 and accepted.json()["status"] == "ACKNOWLEDGED"
        receipt = client.post(
            f"/api/v1/weighment/sessions/{replacement_code}/receipt", headers=farmer_headers
        )
        assert receipt.status_code == 200
        assert receipt.json()["qr_payload"].startswith(f"pashusetu://weighment/{replacement_code}")
        assert replacement.status == "VERIFIED"
    finally:
        app.dependency_overrides.clear()
        db.close()
        transaction.rollback()
        connection.close()
