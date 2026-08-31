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
    EvidenceAddResponse,
    ReweighAttachRequest,
    ReweighAttachResponse,
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


def _transaction_or_404(db: Session, dispute: Dispute) -> Transaction:
    tx = db.get(Transaction, dispute.transaction_id)
    if tx is None:
        raise AppError("TRANSACTION_NOT_FOUND", "Transaction not found.", 404)
    return tx


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


@router.post("/{dispute_id}/evidence", response_model=EvidenceAddResponse)
def post_evidence(
    dispute_id: str,
    payload: EvidenceAddRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    dispute = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not dispute:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = _transaction_or_404(db, dispute)
    transaction_for_party(db, tx.transaction_code, user.id)
    row = add_evidence(
        db,
        dispute,
        user.id,
        payload.evidence_type,
        payload.evidence_reference,
    )
    return EvidenceAddResponse(evidence_id=str(row.id), status="RECORDED")


@router.post("/{dispute_id}/reweigh", response_model=ReweighAttachResponse)
def post_reweigh(
    dispute_id: str,
    payload: ReweighAttachRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    dispute = db.scalar(select(Dispute).where(Dispute.dispute_code == dispute_id))
    if not dispute:
        raise AppError("DISPUTE_NOT_FOUND", "Dispute not found.", 404)
    tx = _transaction_or_404(db, dispute)
    transaction_for_party(db, tx.transaction_code, user.id)
    row = attach_reweigh(db, dispute, user.id, payload.weighment_id, payload.stage)
    return ReweighAttachResponse(
        reweigh_id=str(row.id),
        stage=row.stage,
        status=row.status,
    )


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
    tx = _transaction_or_404(db, dispute)
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
