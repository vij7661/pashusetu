from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.livestock.models import EvidenceAsset, Goat, Lot
from app.weighment.models import (
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
)
from app.weighment.schemas import (
    AcknowledgeRequest,
    FarmerWeighmentReviewResponse,
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


def _farmer_for_user(db: Session, user: User) -> FarmerProfile:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if farmer is None:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 403)
    return farmer


def _farmer_owned_session(
    db: Session,
    code: str,
    user: User,
) -> tuple[WeighmentSession, FarmerProfile]:
    session = _session_by_code(db, code)
    farmer = _farmer_for_user(db, user)
    if session.farmer_profile_id != farmer.id:
        raise AppError(
            "WEIGHMENT_NOT_OWNED",
            "This weighment does not belong to the authenticated Farmer.",
            403,
        )
    return session, farmer


def _target_code(db: Session, session: WeighmentSession) -> str:
    if session.target_type == "GOAT":
        target = db.get(Goat, session.target_id)
        if target is None:
            raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Goat not found.", 404)
        return target.goat_code
    target = db.get(Lot, session.target_id)
    if target is None:
        raise AppError("WEIGHMENT_TARGET_NOT_FOUND", "Lot not found.", 404)
    return target.lot_code


def _farmer_review_response(
    db: Session,
    session: WeighmentSession,
) -> FarmerWeighmentReviewResponse:
    locked = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session.id,
            WeightReading.locked.is_(True),
        )
    )
    if locked is None:
        raise AppError("LOCKED_READING_NOT_FOUND", "Locked reading not found.", 409)

    centre = db.get(MandalCentre, session.centre_id)
    operator = db.get(OperatorProfile, session.operator_id)
    scale = db.get(ScaleDevice, session.scale_id)
    evidence = db.scalar(
        select(EvidenceAsset).where(
            EvidenceAsset.owner_type == "WEIGHMENT",
            EvidenceAsset.owner_id == session.id,
            EvidenceAsset.evidence_type == "WEIGHMENT_VIDEO",
        )
    )
    return FarmerWeighmentReviewResponse(
        weighment_id=session.weighment_code,
        target_type=session.target_type,
        target_id=_target_code(db, session),
        centre_code=centre.centre_code,
        centre_name=centre.name,
        operator_code=operator.operator_code,
        scale_code=scale.scale_code,
        net_kg=locked.net_kg,
        verification_evidence_present=evidence is not None,
        status=session.status,
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


@router.get(
    "/farmer-reviews",
    response_model=list[FarmerWeighmentReviewResponse],
)
def farmer_reviews(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    farmer = _farmer_for_user(db, user)
    sessions = db.scalars(
        select(WeighmentSession)
        .where(
            WeighmentSession.farmer_profile_id == farmer.id,
            WeighmentSession.status == "FARMER_REVIEW",
        )
        .order_by(WeighmentSession.created_at.desc())
    ).all()
    return [_farmer_review_response(db, session) for session in sessions]


@router.get(
    "/sessions/{weighment_id}/farmer-review",
    response_model=FarmerWeighmentReviewResponse,
)
def farmer_review(
    weighment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    session, _ = _farmer_owned_session(db, weighment_id, user)
    return _farmer_review_response(db, session)


@router.post("/sessions/{weighment_id}/readings", response_model=ReadingResponse, status_code=201)
def post_reading(
    weighment_id: str,
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s = _session_by_code(db, weighment_id)
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
    evidence = attach_verification_video(db, s, UUID(payload.video_evidence_id))
    return {"evidence_id": str(evidence.id), "status": s.status}


@router.post("/sessions/{weighment_id}/acknowledge")
def post_acknowledge(
    weighment_id: str,
    payload: AcknowledgeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s, _ = _farmer_owned_session(db, weighment_id, user)
    ack = acknowledge_weighment(db, s, payload.acknowledged, payload.method)
    return {"acknowledgement_id": str(ack.id), "status": s.status}


@router.post("/sessions/{weighment_id}/receipt", response_model=ReceiptResponse)
def post_receipt(
    weighment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    s, _ = _farmer_owned_session(db, weighment_id, user)
    receipt = create_receipt(db, s)
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
    user: User = Depends(current_user),
):
    previous = _session_by_code(db, weighment_id)
    if previous.status not in {"REJECTED_BY_FARMER", "DISPUTED"}:
        raise AppError("REWEIGH_NOT_ALLOWED", "Reweigh is not allowed in the current state.", 409)

    target_code = _target_code(db, previous)
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
