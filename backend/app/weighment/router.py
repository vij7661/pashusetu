from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.core.enums import Role
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.livestock.models import Goat, Lot
from app.weighment.models import MandalCentre, OperatorProfile, ScaleDevice, WeighmentSession
from app.weighment.schemas import (
    AcknowledgeRequest,
    LockReadingRequest,
    ReadingCreate,
    ReadingResponse,
    ReceiptResponse,
    ReweighRequest,
    VerificationEvidenceRequest,
    WeighmentSessionResponse,
    WeighmentStartRequest,
)
from app.weighment.service import (
    acknowledge_weighment,
    append_reading,
    attach_verification_video,
    create_receipt,
    lock_reading,
    start_weighment,
)

router = APIRouter(prefix="/weighment", tags=["weighment"])
operator_required = require_roles(Role.OPERATOR)
farmer_required = require_roles(Role.FARMER)


def _session_by_code(db: Session, code: str) -> WeighmentSession:
    session = db.scalar(select(WeighmentSession).where(WeighmentSession.weighment_code == code))
    if not session:
        raise AppError("WEIGHMENT_NOT_FOUND", "Weighment session not found.", 404)
    return session


def _session_response(db: Session, session: WeighmentSession) -> WeighmentSessionResponse:
    operator = db.get(OperatorProfile, session.operator_id)
    centre = db.get(MandalCentre, session.centre_id)
    scale = db.get(ScaleDevice, session.scale_id)
    return WeighmentSessionResponse(
        weighment_id=session.weighment_code,
        target_type=session.target_type,
        target_id=str(session.target_id),
        centre_code=centre.centre_code,
        operator_code=operator.operator_code,
        scale_code=scale.scale_code,
        status=session.status,
        reweigh_of_id=str(session.reweigh_of_id) if session.reweigh_of_id else None,
    )


def _require_farmer_session_owner(db: Session, session: WeighmentSession, user: User) -> FarmerProfile:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if not farmer:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 409)

    if session.target_type == "GOAT":
        target = db.get(Goat, session.target_id)
    elif session.target_type == "LOT":
        target = db.get(Lot, session.target_id)
    else:
        target = None

    if target is None:
        raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Weighment target not found.", 404)
    if target.farmer_profile_id != farmer.id:
        raise AppError("WEIGHMENT_FORBIDDEN", "This weighment does not belong to the current Farmer.", 403)
    return farmer


@router.post("/sessions", response_model=WeighmentSessionResponse, status_code=201)
def create_session(
    payload: WeighmentStartRequest,
    db: Session = Depends(get_db),
    user: User = Depends(operator_required),
):
    session = start_weighment(
        db,
        operator_user_id=user.id,
        target_type=payload.target_type,
        target_code=payload.target_id,
        scale_code=payload.scale_code,
    )
    return _session_response(db, session)


@router.post("/sessions/{weighment_id}/readings", response_model=ReadingResponse, status_code=201)
def post_reading(
    weighment_id: str,
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(operator_required),
):
    session = _session_by_code(db, weighment_id)
    reading = append_reading(db, session, payload)
    return ReadingResponse(
        reading_id=str(reading.id),
        sequence_no=reading.sequence_no,
        gross_kg=reading.gross_kg,
        tare_kg=reading.tare_kg,
        net_kg=reading.net_kg,
        stable=reading.stable,
        locked=reading.locked,
    )


@router.post("/sessions/{weighment_id}/lock", response_model=ReadingResponse)
def post_lock(
    weighment_id: str,
    payload: LockReadingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(operator_required),
):
    session = _session_by_code(db, weighment_id)
    reading = lock_reading(db, session, UUID(payload.reading_id))
    return ReadingResponse(
        reading_id=str(reading.id),
        sequence_no=reading.sequence_no,
        gross_kg=reading.gross_kg,
        tare_kg=reading.tare_kg,
        net_kg=reading.net_kg,
        stable=reading.stable,
        locked=reading.locked,
    )


@router.post("/sessions/{weighment_id}/verification-video")
def post_verification_video(
    weighment_id: str,
    payload: VerificationEvidenceRequest,
    db: Session = Depends(get_db),
    user: User = Depends(operator_required),
):
    session = _session_by_code(db, weighment_id)
    evidence = attach_verification_video(db, session, UUID(payload.video_evidence_id))
    return {"evidence_id": str(evidence.id), "status": session.status}


@router.post("/sessions/{weighment_id}/acknowledge")
def post_acknowledge(
    weighment_id: str,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(farmer_required),
):
    session = _session_by_code(db, weighment_id)
    _require_farmer_session_owner(db, session, user)
    acknowledgement = acknowledge_weighment(db, session, payload.acknowledged, payload.method)
    return {"acknowledgement_id": str(acknowledgement.id), "status": session.status}


@router.post("/sessions/{weighment_id}/receipt", response_model=ReceiptResponse)
def post_receipt(
    weighment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(farmer_required),
):
    session = _session_by_code(db, weighment_id)
    _require_farmer_session_owner(db, session, user)
    receipt = create_receipt(db, session)
    return ReceiptResponse(
        receipt_id=str(receipt.id),
        receipt_code=receipt.receipt_code,
        qr_payload=receipt.qr_payload,
        print_status=receipt.print_status,
    )


@router.post("/sessions/{weighment_id}/reweigh", response_model=WeighmentSessionResponse, status_code=201)
def post_reweigh(
    weighment_id: str,
    payload: ReweighRequest,
    db: Session = Depends(get_db),
    user: User = Depends(operator_required),
):
    previous = _session_by_code(db, weighment_id)
    if previous.status not in {"REJECTED_BY_FARMER", "DISPUTED"}:
        raise AppError("REWEIGH_NOT_ALLOWED", "Reweigh is not allowed in the current state.", 409)

    if previous.target_type == "GOAT":
        target = db.get(Goat, previous.target_id)
        if target is None:
            raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Goat not found.", 404)
        target_code = target.goat_code
    else:
        target = db.get(Lot, previous.target_id)
        if target is None:
            raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Lot not found.", 404)
        target_code = target.lot_code

    session = start_weighment(
        db,
        operator_user_id=user.id,
        target_type=previous.target_type,
        target_code=target_code,
        scale_code=payload.scale_code,
        reweigh_of=previous,
    )
    session.status = "REWEIGH_LIVE"
    db.commit()
    db.refresh(session)
    return _session_response(db, session)
