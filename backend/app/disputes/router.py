from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_farmer_kyc_verified, require_roles
from app.core.enums import Role
from app.core.errors import AppError
from app.db.session import get_db
from app.disputes.models import Dispute
from app.disputes.schemas import (
    DisputeOpenRequest,
    DisputeResolveRequest,
    DisputeResponse,
    EvidenceAddRequest,
    ReweighAttachRequest,
)
from app.disputes.service import add_evidence, attach_reweigh, open_dispute, resolve_dispute
from app.identity.models import User
from app.transaction.models import Transaction
from app.transaction.service import transaction_for_party

router = APIRouter(prefix="/disputes", tags=["disputes"])
platform_resolver_required = require_roles(Role.ADMIN, Role.OPERATOR)


def _response(tx: Transaction, dispute: Dispute) -> DisputeResponse:
    return DisputeResponse(
        dispute_id=dispute.dispute_code,
        transaction_id=tx.transaction_code,
        reason=dispute.reason,
        disputed_amount_paise=dispute.disputed_amount_paise,
        status=dispute.status,
        settlement_adjustment_paise=dispute.settlement_adjustment_paise,
        final_decision=dispute.final_decision,
    )


@router.post("/transactions/{transaction_id}", response_model=DisputeResponse, status_code=201)
def post_dispute(
    transaction_id: str,
    payload: DisputeOpenRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    dispute = open_dispute(
        db,
        tx,
        user.id,
        payload.reason,
        payload.disputed_amount_paise,
    )
    return _response(tx, dispute)


@router.post("/{dispute_id}/evidence")
def post_evidence(
    dispute_id: str,
    payload: EvidenceAddRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    dispute = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not dispute:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = db.get(Transaction, dispute.transaction_id)
    transaction_for_party(db, tx.transaction_code, user.id)
    row = add_evidence(db, dispute, payload.evidence_type, payload.evidence_reference)
    return {"evidence_id": str(row.id), "status": "RECORDED"}


@router.post("/{dispute_id}/reweigh")
def post_reweigh(
    dispute_id: str,
    payload: ReweighAttachRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    dispute = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not dispute:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = db.get(Transaction, dispute.transaction_id)
    transaction_for_party(db, tx.transaction_code, user.id)
    row = attach_reweigh(db, dispute, payload.weighment_id, payload.stage)
    return {"reweigh_id": str(row.id), "stage": row.stage, "status": row.status}


@router.post("/{dispute_id}/resolve", response_model=DisputeResponse)
def post_resolve(
    dispute_id: str,
    payload: DisputeResolveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(platform_resolver_required),
):
    dispute = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not dispute:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = db.get(Transaction, dispute.transaction_id)
    dispute = resolve_dispute(
        db,
        tx,
        dispute,
        user.id,
        payload.final_decision,
        payload.settlement_adjustment_paise,
        payload.resolution_rule,
    )
    return _response(tx, dispute)
