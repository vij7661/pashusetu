from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.core.errors import AppError
from app.identity.profile_models import FarmerProfile
from app.livestock.models import EvidenceAsset, Goat, Lot
from app.weighment.models import (
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
    FarmerWeighmentAcknowledgement,
    WeighmentReceipt,
)
from app.weighment.schemas import ReadingCreate


def operator_for_user(db: Session, user_id: UUID) -> OperatorProfile:
    operator = db.scalar(select(OperatorProfile).where(OperatorProfile.user_id == user_id))
    if not operator or not operator.active:
        raise AppError("OPERATOR_REQUIRED", "Active operator profile is required.", 403)
    return operator


def resolve_target(db: Session, target_type: str, target_code: str):
    if target_type == "GOAT":
        target = db.scalar(select(Goat).where(Goat.goat_code == target_code))
    else:
        target = db.scalar(select(Lot).where(Lot.lot_code == target_code))
    if not target:
        raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Goat or lot not found.", 404)
    return target


def resolve_scale_for_operator(db: Session, operator: OperatorProfile, scale_code: str) -> ScaleDevice:
    scale = db.scalar(
        select(ScaleDevice).where(
            ScaleDevice.scale_code == scale_code,
            ScaleDevice.centre_id == operator.centre_id,
            ScaleDevice.active.is_(True),
        )
    )
    if not scale:
        raise AppError("SCALE_NOT_AVAILABLE", "Scale is not registered for this centre.", 409)
    if scale.calibration_status != "VALID":
        raise AppError("SCALE_CALIBRATION_INVALID", "Scale calibration is not valid.", 409)
    return scale


def start_weighment(
    db: Session,
    operator_user_id: UUID,
    target_type: str,
    target_code: str,
    scale_code: str,
    reweigh_of: WeighmentSession | None = None,
) -> WeighmentSession:
    operator = operator_for_user(db, operator_user_id)
    target = resolve_target(db, target_type, target_code)
    scale = resolve_scale_for_operator(db, operator, scale_code)

    session = WeighmentSession(
        weighment_code=f"WG-{uuid4().hex[:10].upper()}",
        target_type=target_type,
        target_id=target.id,
        farmer_profile_id=target.farmer_profile_id,
        operator_id=operator.id,
        centre_id=operator.centre_id,
        scale_id=scale.id,
        status="LIVE",
        reweigh_of_id=reweigh_of.id if reweigh_of else None,
    )
    db.add(session)
    db.flush()
    append_event(
        db,
        "WEIGHMENT",
        session.id,
        "WEIGHMENT_STARTED",
        actor_user_id=operator_user_id,
        payload={
            "status": session.status,
            "target_type": target_type,
            "target_id": str(target.id),
            "centre_id": str(operator.centre_id),
            "scale_id": str(scale.id),
            "reweigh_of_id": str(reweigh_of.id) if reweigh_of else None,
        },
        commit=False,
    )
    db.commit()
    db.refresh(session)
    return session


def append_reading(db: Session, session: WeighmentSession, payload: ReadingCreate) -> WeightReading:
    if session.status not in {"LIVE", "REWEIGH_LIVE"}:
        raise AppError("WEIGHMENT_NOT_LIVE", "Weighment is not accepting readings.", 409)

    next_sequence = db.scalar(
        select(func.coalesce(func.max(WeightReading.sequence_no), 0) + 1)
        .where(WeightReading.weighment_session_id == session.id)
    )
    reading = WeightReading(
        weighment_session_id=session.id,
        sequence_no=next_sequence,
        gross_kg=payload.gross_kg,
        tare_kg=payload.tare_kg,
        net_kg=payload.gross_kg - payload.tare_kg,
        stable=payload.stable,
        locked=False,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def lock_reading(db: Session, session: WeighmentSession, reading_id: UUID) -> WeightReading:
    if session.status not in {"LIVE", "REWEIGH_LIVE"}:
        raise AppError("WEIGHMENT_NOT_LIVE", "Weighment is not live.", 409)

    already_locked = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session.id,
            WeightReading.locked.is_(True),
        )
    )
    if already_locked:
        raise AppError("WEIGHMENT_ALREADY_LOCKED", "A reading is already locked.", 409)

    reading = db.scalar(
        select(WeightReading).where(
            WeightReading.id == reading_id,
            WeightReading.weighment_session_id == session.id,
        )
    )
    if not reading:
        raise AppError("READING_NOT_FOUND", "Weight reading not found.", 404)
    if not reading.stable:
        raise AppError("READING_NOT_STABLE", "Only a stable reading may be locked.", 409)

    reading.locked = True
    session.status = "WEIGHT_LOCKED"
    db.commit()
    db.refresh(reading)
    return reading


def attach_verification_video(
    db: Session,
    session: WeighmentSession,
    evidence_id: UUID,
) -> EvidenceAsset:
    if session.status != "WEIGHT_LOCKED":
        raise AppError("WEIGHT_NOT_LOCKED", "Lock a stable weight before verification video.", 409)

    evidence = db.get(EvidenceAsset, evidence_id)
    if not evidence:
        raise AppError("EVIDENCE_NOT_FOUND", "Evidence asset not found.", 404)

    evidence.owner_type = "WEIGHMENT"
    evidence.owner_id = session.id
    evidence.evidence_type = "WEIGHMENT_VIDEO"
    session.status = "FARMER_REVIEW"
    db.commit()
    db.refresh(evidence)
    return evidence


def acknowledge_weighment(
    db: Session,
    session: WeighmentSession,
    acknowledged: bool,
    method: str,
    *,
    actor_user_id: UUID | None = None,
) -> FarmerWeighmentAcknowledgement | None:
    if session.status != "FARMER_REVIEW":
        raise AppError("WEIGHMENT_NOT_READY_FOR_ACK", "Weighment is not ready for farmer acknowledgement.", 409)

    if not acknowledged:
        session.status = "REJECTED_BY_FARMER"
        append_event(
            db,
            "WEIGHMENT",
            session.id,
            "FARMER_WEIGHMENT_REJECTED",
            actor_user_id=actor_user_id,
            payload={"method": method, "status": session.status},
            commit=False,
        )
        db.commit()
        return None

    ack = FarmerWeighmentAcknowledgement(
        weighment_session_id=session.id,
        farmer_profile_id=session.farmer_profile_id,
        acknowledged=True,
        method=method,
    )
    db.add(ack)
    session.status = "ACKNOWLEDGED"
    db.flush()
    append_event(
        db,
        "WEIGHMENT",
        session.id,
        "FARMER_WEIGHMENT_ACKNOWLEDGED",
        actor_user_id=actor_user_id,
        payload={"method": method, "status": session.status},
        commit=False,
    )
    db.commit()
    db.refresh(ack)
    return ack


def create_receipt(
    db: Session,
    session: WeighmentSession,
    *,
    actor_user_id: UUID | None = None,
) -> WeighmentReceipt:
    if session.status != "ACKNOWLEDGED":
        raise AppError("ACK_REQUIRED", "Farmer acknowledgement is required before receipt generation.", 409)

    locked = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session.id,
            WeightReading.locked.is_(True),
        )
    )
    if not locked:
        raise AppError("LOCKED_READING_NOT_FOUND", "Locked reading not found.", 500)

    receipt = db.scalar(
        select(WeighmentReceipt).where(WeighmentReceipt.weighment_session_id == session.id)
    )
    if receipt:
        return receipt

    receipt = WeighmentReceipt(
        weighment_session_id=session.id,
        receipt_code=f"RCPT-{uuid4().hex[:10].upper()}",
        qr_payload=(
            f"pashusetu://weighment/{session.weighment_code}"
            f"?net_kg={locked.net_kg}&scale_id={session.scale_id}"
        ),
        print_status="READY",
    )
    db.add(receipt)
    session.status = "VERIFIED"
    db.flush()
    append_event(
        db,
        "WEIGHMENT",
        session.id,
        "WEIGHMENT_RECEIPT_CREATED",
        actor_user_id=actor_user_id,
        payload={"status": session.status},
        commit=False,
    )
    db.commit()
    db.refresh(receipt)
    return receipt
