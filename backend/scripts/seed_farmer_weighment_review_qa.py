"""Seed a Farmer-owned weighment awaiting explicit review.

Development/test only. The fixture is intentionally separate from production flows so
manual QA can exercise accept and reject decisions without operating the Operator app.
"""

from decimal import Decimal

from sqlalchemy import select

from app.auth.service import DEVELOPMENT_ENVS
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.identity.profile_models import FarmerProfile
from app.livestock.models import EvidenceAsset, Goat
from app.weighment.models import (
    FarmerWeighmentAcknowledgement,
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
)

FARMER_CODE = "F-FV2-033"
GOAT_CODE = "GOAT-QA-ACK"
WEIGHMENT_CODE = "WG-QA-ACK-001"
CENTRE_CODE = "QA-CHY-01"
OPERATOR_CODE = "OP-QA-001"
SCALE_CODE = "QA-SCALE-01"


def seed_weighment_review() -> None:
    settings = get_settings()
    if settings.app_env.lower() not in DEVELOPMENT_ENVS:
        raise RuntimeError(
            "Farmer weighment-review QA fixtures are forbidden outside "
            "local/test/development."
        )

    db = SessionLocal()
    try:
        farmer = db.scalar(
            select(FarmerProfile).where(FarmerProfile.farmer_code == FARMER_CODE)
        )
        centre = db.scalar(
            select(MandalCentre).where(MandalCentre.centre_code == CENTRE_CODE)
        )
        operator = db.scalar(
            select(OperatorProfile).where(OperatorProfile.operator_code == OPERATOR_CODE)
        )
        scale = db.scalar(
            select(ScaleDevice).where(ScaleDevice.scale_code == SCALE_CODE)
        )
        if farmer is None or centre is None or operator is None or scale is None:
            raise RuntimeError(
                "Run scripts/seed_farmer_manual_qa.py before the Farmer weighment-review seed."
            )

        goat = db.scalar(select(Goat).where(Goat.goat_code == GOAT_CODE))
        if goat is None:
            goat = Goat(
                goat_code=GOAT_CODE,
                farmer_profile_id=farmer.id,
                breed="Sirohi",
                sex="MALE",
                age_months=18,
                status="WEIGHMENT_REVIEW",
            )
            db.add(goat)
            db.flush()

        session = db.scalar(
            select(WeighmentSession).where(
                WeighmentSession.weighment_code == WEIGHMENT_CODE
            )
        )
        if session is None:
            session = WeighmentSession(
                weighment_code=WEIGHMENT_CODE,
                target_type="GOAT",
                target_id=goat.id,
                farmer_profile_id=farmer.id,
                operator_id=operator.id,
                centre_id=centre.id,
                scale_id=scale.id,
                status="FARMER_REVIEW",
            )
            db.add(session)
            db.flush()

        locked = db.scalar(
            select(WeightReading).where(
                WeightReading.weighment_session_id == session.id,
                WeightReading.locked.is_(True),
            )
        )
        if locked is None:
            db.add(
                WeightReading(
                    weighment_session_id=session.id,
                    sequence_no=1,
                    gross_kg=Decimal("47.250"),
                    tare_kg=Decimal("0.000"),
                    net_kg=Decimal("47.250"),
                    stable=True,
                    locked=True,
                )
            )

        evidence = db.scalar(
            select(EvidenceAsset).where(
                EvidenceAsset.owner_type == "WEIGHMENT",
                EvidenceAsset.owner_id == session.id,
                EvidenceAsset.evidence_type == "WEIGHMENT_VIDEO",
            )
        )
        if evidence is None:
            db.add(
                EvidenceAsset(
                    owner_type="WEIGHMENT",
                    owner_id=session.id,
                    evidence_type="WEIGHMENT_VIDEO",
                    storage_key="qa/weighment/WG-QA-ACK-001/video.mp4",
                    mime_type="video/mp4",
                    sha256_hex=None,
                    captured_by_user_id=operator.user_id,
                    status="UPLOADED",
                )
            )

        decision = db.scalar(
            select(FarmerWeighmentAcknowledgement).where(
                FarmerWeighmentAcknowledgement.weighment_session_id == session.id
            )
        )
        if decision is not None:
            raise RuntimeError(
                f"{WEIGHMENT_CODE} has already been decided. Reset the QA database "
                "with `docker compose down -v` before re-running accept/reject QA."
            )

        db.commit()
        print("Farmer weighment-review fixture ready")
        print(f"{WEIGHMENT_CODE} / {GOAT_CODE} / 47.250 kg / FARMER_REVIEW")
    finally:
        db.close()


if __name__ == "__main__":
    seed_weighment_review()
