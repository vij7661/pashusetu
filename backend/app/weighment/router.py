from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.weighment.models import MandalCentre, OperatorProfile, ScaleDevice, WeighmentSession
from app.weighment.schemas import (
    AcknowledgeRequest,
    LockReadingRequest,
    ReadingCreate,
    ReadingResponse,
    ReceiptResponse,
    ReweighRequest,
    VerificationEvidenceCreate,
    VerificationEvidenceRequest,
    WeighmentSessionResponse,
    WeighmentStartRequest,
)
from app.weighment.service import (
    acknowledge_weighment,
    append_reading,
    attach_verification_video,
    create_receipt,
    create_verification_evidence,
    lock_reading,
    require_session_farmer,
    require_session_operator,
    start_weighment,
)

router = APIRouter(prefix="/weighment", tags=["weighment"])


def _session_by_code(db: Session, code: str) -> WeighmentSession:
    s = db.scalar(select(WeighmentSession).where(WeighmentSession.weighment_code == code))
    if not s:
        raise AppError("WEIGHMENT_NOT_FOUND", "Weighment session not found.", 404)
    return s


def _session_response(db: Session, s: WeighmentSession) -> WeighmentSessionResponse:
    operator = db.get(OperatorProfile, s.operator_id)
    centre = db.get(MandalCentre, s.centre_id)
    scale = db.get(ScaleDevice, s.scale_id)
    return WeighmentSessionResponse(
        weighment_id=s.weighment_code,
        target_type=s.target_type,
        target_id=str(s.target_id),
        centre_code=centre.centre_code,
        operator_code=operator.operator_code,
        scale_code=scale.scale_code,
        status=s.status,
        reweigh_of_id=str(s.reweigh_of_id) if s.reweigh_of_id else None,
    )


@router.post("/sessions", response_model=WeighmentSessionResponse, status_code=201)
def create_session(
    payload: WeighmentStartRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = start_weighment(
        db,
        operator_user_id=user.id,
        target_type=payload.target_type,
        target_code=payload.target_id,
        scale_code=payload.scale_code,
    )
    return _session_response(db, s)


@router.post("/sessions/{weighment_id}/readings", response_model=ReadingResponse, status_code=201)
def post_reading(
    weighment_id: str,
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    require_session_operator(db, s, user.id)
    r = append_reading(db, s, payload)
    return ReadingResponse(
        reading_id=str(r.id),
        sequence_no=r.sequence_no,
        gross_kg=r.gross_kg,
        tare_kg=r.tare_kg,
        net_kg=r.net_kg,
        stable=r.stable,
        locked=r.locked,
    )


@router.post("/sessions/{weighment_id}/lock", response_model=ReadingResponse)
def post_lock(
    weighment_id: str,
    payload: LockReadingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    require_session_operator(db, s, user.id)
    r = lock_reading(db, s, UUID(payload.reading_id))
    return ReadingResponse(
        reading_id=str(r.id),
        sequence_no=r.sequence_no,
        gross_kg=r.gross_kg,
        tare_kg=r.tare_kg,
        net_kg=r.net_kg,
        stable=r.stable,
        locked=r.locked,
    )


@router.post("/sessions/{weighment_id}/verification-video")
def post_verification_video(
    weighment_id: str,
    payload: VerificationEvidenceRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    require_session_operator(db, s, user.id)
    evidence = attach_verification_video(db, s, UUID(payload.video_evidence_id))
    return {"evidence_id": str(evidence.id), "status": s.status}


@router.post("/sessions/{weighment_id}/verification-evidence", status_code=201)
def post_verification_evidence(
    weighment_id: str,
    payload: VerificationEvidenceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    evidence = create_verification_evidence(db, s, user.id, payload.file_name, payload.mime_type)
    return {
        "evidence_id": str(evidence.id),
        "upload_method": "PUT",
        "upload_url": f"http://localhost:8000/dev-upload/{evidence.id}",
        "status": evidence.status,
    }


@router.post("/sessions/{weighment_id}/acknowledge")
def post_acknowledge(
    weighment_id: str,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    require_session_farmer(db, s, user.id)
    ack = acknowledge_weighment(db, s, payload.acknowledged, payload.method)
    return {"acknowledgement_id": str(ack.id) if ack else None, "status": s.status}


@router.post("/sessions/{weighment_id}/receipt", response_model=ReceiptResponse)
def post_receipt(
    weighment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
    require_session_farmer(db, s, user.id)
    receipt = create_receipt(db, s)
    return ReceiptResponse(
        receipt_id=str(receipt.id),
        receipt_code=receipt.receipt_code,
        qr_payload=receipt.qr_payload,
        print_status=receipt.print_status,
    )


@router.post(
    "/sessions/{weighment_id}/reweigh", response_model=WeighmentSessionResponse, status_code=201
)
def post_reweigh(
    weighment_id: str,
    payload: ReweighRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    previous = _session_by_code(db, weighment_id)
    require_session_operator(db, previous, user.id)
    if previous.status not in {"REJECTED_BY_FARMER", "DISPUTED"}:
        raise AppError("REWEIGH_NOT_ALLOWED", "Reweigh is not allowed in the current state.", 409)

    target_code = str(previous.target_id)
    # Resolve target code from persisted target entity.
    from app.livestock.models import Goat, Lot

    if previous.target_type == "GOAT":
        target = db.get(Goat, previous.target_id)
        target_code = target.goat_code
    else:
        target = db.get(Lot, previous.target_id)
        target_code = target.lot_code

    s = start_weighment(
        db,
        operator_user_id=user.id,
        target_type=previous.target_type,
        target_code=target_code,
        scale_code=payload.scale_code,
        reweigh_of=previous,
    )
    s.status = "REWEIGH_LIVE"
    db.commit()
    db.refresh(s)
    return _session_response(db, s)
