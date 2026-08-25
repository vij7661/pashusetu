from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.db.session import get_db
from app.identity.models import User
from app.core.errors import AppError
from app.transaction.service import transaction_for_party
from app.disputes.models import Dispute
from app.disputes.schemas import (
    DisputeOpenRequest,
    EvidenceAddRequest,
    ReweighAttachRequest,
    DisputeResolveRequest,
    DisputeResponse,
)
from app.disputes.service import open_dispute, add_evidence, attach_reweigh, resolve_dispute

router = APIRouter(prefix="/disputes", tags=["disputes"])


def _response(tx, d):
    return DisputeResponse(
        dispute_id=d.dispute_code,
        transaction_id=tx.transaction_code,
        reason=d.reason,
        disputed_amount_paise=d.disputed_amount_paise,
        status=d.status,
        settlement_adjustment_paise=d.settlement_adjustment_paise,
        final_decision=d.final_decision,
    )


@router.post("/transactions/{transaction_id}", response_model=DisputeResponse, status_code=201)
def post_dispute(
    transaction_id: str,
    payload: DisputeOpenRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    d = open_dispute(db, tx, user.id, payload.reason, payload.disputed_amount_paise)
    return _response(tx, d)


@router.post("/{dispute_id}/evidence")
def post_evidence(
    dispute_id: str,
    payload: EvidenceAddRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    d = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not d:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    row = add_evidence(db, d, payload.evidence_type, payload.evidence_reference)
    return {"evidence_id": str(row.id), "status": "RECORDED"}


@router.post("/{dispute_id}/reweigh")
def post_reweigh(
    dispute_id: str,
    payload: ReweighAttachRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    d = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not d:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    row = attach_reweigh(db, d, payload.weighment_id, payload.stage)
    return {"reweigh_id": str(row.id), "stage": row.stage, "status": row.status}


@router.post("/{dispute_id}/resolve", response_model=DisputeResponse)
def post_resolve(
    dispute_id: str,
    payload: DisputeResolveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    d = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not d:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = db.get(__import__("app.transaction.models", fromlist=["Transaction"]).Transaction, d.transaction_id)
    d = resolve_dispute(
        db, tx, d, user.id, payload.final_decision,
        payload.settlement_adjustment_paise, payload.resolution_rule,
    )
    return _response(tx, d)
