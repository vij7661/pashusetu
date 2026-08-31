from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.auth.dependencies import require_farmer_kyc_verified
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.logistics.models import DeliveryRecord, PickupRecord, TransportAssignment
from app.logistics.schemas import (
    DeliveryRequest,
    PickupRequest,
    PickupResponse,
    ToleranceResult,
    TransportAssignRequest,
    TransportAssignResponse,
)
from app.logistics.service import evaluate_delivery
from app.transaction.service import transaction_for_party, transition_transaction
from app.weighment.models import WeighmentSession

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.post(
    "/transactions/{transaction_id}/transport",
    response_model=TransportAssignResponse,
)
def assign_transport(
    transaction_id: str,
    payload: TransportAssignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "FUNDS_SECURED":
        raise AppError(
            "FUNDS_NOT_SECURED",
            "Funds must be secured before pickup scheduling.",
            409,
        )
    assignment = TransportAssignment(
        transaction_id=tx.id,
        transporter_name=payload.transporter_name,
        driver_name=payload.driver_name,
        driver_phone=payload.driver_phone,
        vehicle_number=payload.vehicle_number,
    )
    db.add(assignment)
    db.flush()
    transition_transaction(db, tx, "PICKUP_SCHEDULED", commit=False)
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "TRANSPORT_ASSIGNED",
        user.id,
        payload={"assignment_id": str(assignment.id)},
        commit=False,
    )
    db.commit()
    return TransportAssignResponse(
        assignment_id=str(assignment.id),
        transaction_state=tx.state,
    )


@router.post(
    "/transactions/{transaction_id}/pickup",
    response_model=PickupResponse,
)
def pickup(
    transaction_id: str,
    payload: PickupRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "PICKUP_SCHEDULED":
        raise AppError("PICKUP_NOT_READY", "Pickup is not scheduled.", 409)
    if not payload.qr_verified:
        raise AppError("QR_REQUIRED", "QR verification is required at pickup.", 409)
    record = PickupRecord(
        transaction_id=tx.id,
        qr_verified=True,
        goat_count=payload.goat_count,
        loading_video_evidence_id=payload.loading_video_evidence_id,
        departure_note=payload.departure_note,
    )
    db.add(record)
    db.flush()
    transition_transaction(db, tx, "PICKED_UP", commit=False)
    transition_transaction(db, tx, "IN_TRANSIT", commit=False)
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "PICKUP_RECORDED",
        user.id,
        payload={
            "pickup_id": str(record.id),
            "goat_count": record.goat_count,
            "qr_verified": True,
        },
        commit=False,
    )
    db.commit()
    return PickupResponse(pickup_id=str(record.id), transaction_state=tx.state)


@router.post("/transactions/{transaction_id}/delivery", response_model=ToleranceResult)
def delivery(
    transaction_id: str,
    payload: DeliveryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "IN_TRANSIT":
        raise AppError("DELIVERY_NOT_READY", "Transaction is not in transit.", 409)
    if not payload.qr_verified:
        raise AppError("QR_REQUIRED", "QR verification is required at delivery.", 409)
    weighment = db.get(WeighmentSession, payload.delivery_weighment_id)
    if not weighment or weighment.status != "VERIFIED":
        raise AppError(
            "DELIVERY_WEIGHMENT_REQUIRED",
            "Verified delivery weighment required.",
            409,
        )

    origin, delivered, difference, percent, allowed, within_tolerance = evaluate_delivery(
        db,
        tx,
        weighment,
    )
    record = DeliveryRecord(
        transaction_id=tx.id,
        qr_verified=True,
        goat_count=payload.goat_count,
        delivery_video_evidence_id=payload.delivery_video_evidence_id,
        delivery_weighment_id=weighment.id,
        tolerance_result=(
            "WITHIN_TOLERANCE" if within_tolerance else "OUTSIDE_TOLERANCE"
        ),
    )
    db.add(record)
    db.flush()
    transition_transaction(db, tx, "DELIVERED", commit=False)
    transition_transaction(db, tx, "DELIVERY_VERIFICATION", commit=False)
    transition_transaction(db, tx, "TOLERANCE_CHECK", commit=False)
    transition_transaction(
        db,
        tx,
        "SETTLED" if within_tolerance else "DISPUTED",
        commit=False,
    )
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "DELIVERY_TOLERANCE_EVALUATED",
        user.id,
        payload={
            "delivery_id": str(record.id),
            "delivery_weighment_id": weighment.weighment_code,
            "tolerance_result": record.tolerance_result,
            "transaction_state": tx.state,
        },
        commit=False,
    )
    db.commit()
    return ToleranceResult(
        origin_weight_kg=float(origin),
        delivery_weight_kg=float(delivered),
        difference_kg=float(difference),
        difference_percent=float(percent),
        allowed_percent=float(allowed),
        within_tolerance=within_tolerance,
        route="SETTLEMENT" if within_tolerance else "DISPUTE",
    )
