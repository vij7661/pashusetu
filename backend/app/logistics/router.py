from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.disputes.service import open_dispute
from app.identity.models import User
from app.logistics.models import DeliveryRecord, PickupRecord, TransportAssignment
from app.logistics.schemas import (
    DeliveryRequest,
    PickupRequest,
    ToleranceResult,
    TransportAssignRequest,
)
from app.logistics.service import evaluate_delivery
from app.marketplace.models import Listing
from app.transaction.models import Transaction
from app.transaction.service import transaction_for_party, transition_transaction
from app.weighment.models import OperatorProfile, WeighmentSession

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.post("/transactions/{transaction_id}/transport")
def assign_transport(
    transaction_id: str,
    p: TransportAssignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    tx = db.scalar(select(Transaction).where(Transaction.id == tx.id).with_for_update())
    if tx.state != "FUNDS_SECURED":
        raise AppError("FUNDS_NOT_SECURED", "Funds must be secured before pickup scheduling.", 409)
    a = TransportAssignment(
        transaction_id=tx.id,
        transporter_name=p.transporter_name,
        driver_name=p.driver_name,
        driver_phone=p.driver_phone,
        vehicle_number=p.vehicle_number,
    )
    db.add(a)
    db.commit()
    transition_transaction(db, tx, "PICKUP_SCHEDULED")
    return {"assignment_id": str(a.id), "transaction_state": tx.state}


@router.post("/transactions/{transaction_id}/pickup")
def pickup(
    transaction_id: str,
    p: PickupRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = db.scalar(
        select(Transaction).where(Transaction.transaction_code == transaction_id).with_for_update()
    )
    if not tx:
        raise AppError("TRANSACTION_NOT_FOUND", "Transaction not found.", 404)
    listing = db.get(Listing, tx.listing_id)
    origin_session = db.get(WeighmentSession, listing.weighment_session_id) if listing else None
    operator = db.scalar(
        select(OperatorProfile).where(
            OperatorProfile.user_id == user.id, OperatorProfile.active.is_(True)
        )
    )
    if not operator or not origin_session or operator.id != origin_session.operator_id:
        raise AppError(
            "LISTING_OPERATOR_REQUIRED",
            "Pickup must be recorded by the Operator who verified this listing.",
            403,
        )
    existing = db.scalar(select(PickupRecord).where(PickupRecord.transaction_id == tx.id))
    if existing:
        if existing.idempotency_key != p.idempotency_key:
            raise AppError("PICKUP_ALREADY_RECORDED", "Pickup evidence is immutable.", 409)
        return {"pickup_id": str(existing.id), "transaction_state": tx.state}
    if tx.state != "PICKUP_SCHEDULED":
        raise AppError("PICKUP_NOT_READY", "Pickup is not scheduled.", 409)
    if not p.qr_verified:
        raise AppError("QR_REQUIRED", "QR verification is required at pickup.", 409)
    evidence_id = UUID(p.loading_video_evidence_id)
    r = PickupRecord(
        transaction_id=tx.id,
        qr_verified=True,
        goat_count=p.goat_count,
        loading_video_evidence_id=evidence_id,
        departure_note=p.departure_note,
        recorded_by_user_id=user.id,
        evidence_reference=f"dev://pickup-evidence/{evidence_id}",
        idempotency_key=p.idempotency_key,
    )
    db.add(r)
    db.commit()
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "PICKUP_EVIDENCE_RECORDED",
        user.id,
        payload={"pickup_id": str(r.id), "evidence_reference": r.evidence_reference},
    )
    transition_transaction(db, tx, "PICKED_UP")
    transition_transaction(db, tx, "IN_TRANSIT")
    return {"pickup_id": str(r.id), "transaction_state": tx.state}


@router.post("/transactions/{transaction_id}/delivery", response_model=ToleranceResult)
def delivery(
    transaction_id: str,
    p: DeliveryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = db.scalar(
        select(Transaction).where(Transaction.transaction_code == transaction_id).with_for_update()
    )
    if not tx:
        raise AppError("TRANSACTION_NOT_FOUND", "Transaction not found.", 404)
    ws = db.scalar(
        select(WeighmentSession).where(WeighmentSession.weighment_code == p.delivery_weighment_id)
    )
    if not ws or ws.status != "VERIFIED":
        raise AppError("DELIVERY_WEIGHMENT_REQUIRED", "Verified delivery weighment required.", 409)
    operator = db.scalar(
        select(OperatorProfile).where(
            OperatorProfile.user_id == user.id, OperatorProfile.active.is_(True)
        )
    )
    if not operator or ws.operator_id != operator.id:
        raise AppError(
            "OPERATOR_ONLY",
            "The Operator who verified the final weighment must record delivery.",
            403,
        )
    listing = db.get(Listing, tx.listing_id)
    if (
        not listing
        or ws.farmer_profile_id != tx.farmer_profile_id
        or ws.target_type != listing.target_type
        or ws.target_id != listing.target_id
    ):
        raise AppError(
            "DELIVERY_WEIGHMENT_SCOPE_MISMATCH",
            "Final weighment does not belong to the accepted livestock selection.",
            409,
        )
    existing = db.scalar(select(DeliveryRecord).where(DeliveryRecord.transaction_id == tx.id))
    if existing:
        if existing.idempotency_key != p.idempotency_key:
            raise AppError("DELIVERY_ALREADY_RECORDED", "Delivery decision is immutable.", 409)
        return ToleranceResult(
            origin_weight_kg=float(existing.origin_weight_kg),
            delivery_weight_kg=float(existing.final_weight_kg),
            difference_kg=float(existing.difference_kg),
            difference_percent=float(existing.difference_percent),
            allowed_percent=float(existing.allowed_percent),
            within_tolerance=existing.tolerance_result == "WITHIN_TOLERANCE",
            route="SETTLEMENT" if existing.tolerance_result == "WITHIN_TOLERANCE" else "DISPUTE",
        )
    if tx.state != "IN_TRANSIT":
        raise AppError("DELIVERY_NOT_READY", "Transaction is not in transit.", 409)
    if not p.qr_verified:
        raise AppError("QR_REQUIRED", "QR verification is required at delivery.", 409)
    transition_transaction(db, tx, "DELIVERED")
    transition_transaction(db, tx, "DELIVERY_VERIFICATION")
    transition_transaction(db, tx, "TOLERANCE_CHECK")
    origin, dw, diff, pct, allowed, ok = evaluate_delivery(db, tx, ws)
    evidence_id = UUID(p.delivery_video_evidence_id)
    rec = DeliveryRecord(
        transaction_id=tx.id,
        qr_verified=True,
        goat_count=p.goat_count,
        delivery_video_evidence_id=evidence_id,
        delivery_weighment_id=ws.id,
        tolerance_result="WITHIN_TOLERANCE" if ok else "OUTSIDE_TOLERANCE",
        recorded_by_user_id=user.id,
        evidence_reference=f"dev://delivery-evidence/{evidence_id}",
        idempotency_key=p.idempotency_key,
        origin_weight_kg=origin,
        final_weight_kg=dw,
        difference_kg=diff,
        difference_percent=pct,
        allowed_percent=allowed,
    )
    db.add(rec)
    db.commit()
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "DELIVERY_TOLERANCE_EVALUATED",
        user.id,
        payload={
            "delivery_id": str(rec.id),
            "final_weighment_id": str(ws.id),
            "tolerance_result": rec.tolerance_result,
        },
    )
    transition_transaction(db, tx, "SETTLEMENT_READY" if ok else "DISPUTED")
    if not ok:
        open_dispute(db, tx, user.id, "DELIVERY_WEIGHT_OUTSIDE_TOLERANCE", 0)
    return ToleranceResult(
        origin_weight_kg=float(origin),
        delivery_weight_kg=float(dw),
        difference_kg=float(diff),
        difference_percent=float(pct),
        allowed_percent=float(allowed),
        within_tolerance=ok,
        route="SETTLEMENT" if ok else "DISPUTE",
    )
