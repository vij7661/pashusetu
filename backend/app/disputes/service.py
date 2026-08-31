from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.core.errors import AppError
from app.disputes.models import Dispute, DisputeEvidence, DisputeReweigh
from app.marketplace.models import Listing
from app.transaction.models import Transaction
from app.transaction.service import transition_transaction
from app.weighment.models import WeighmentSession


def _require_open_dispute(dispute: Dispute) -> None:
    if dispute.status != "OPEN":
        raise AppError("DISPUTE_NOT_OPEN", "Dispute is not open for additional evidence.", 409)


def _assert_reweigh_matches_listing(ws: WeighmentSession, listing: Listing) -> None:
    if (
        ws.target_type != listing.target_type
        or ws.target_id != listing.target_id
        or ws.farmer_profile_id != listing.seller_farmer_profile_id
    ):
        raise AppError(
            "REWEIGH_TARGET_MISMATCH",
            "Verified reweigh does not belong to the disputed listing target.",
            409,
        )


def open_dispute(
    db: Session,
    tx: Transaction,
    actor_user_id: UUID,
    reason: str,
    disputed_amount_paise: int,
) -> Dispute:
    existing = db.scalar(select(Dispute).where(Dispute.transaction_id == tx.id))
    if existing:
        return existing
    if tx.state != "DISPUTED":
        raise AppError("TRANSACTION_NOT_DISPUTED", "Transaction is not in disputed state.", 409)

    dispute = Dispute(
        dispute_code=f"DSP-{uuid4().hex[:10].upper()}",
        transaction_id=tx.id,
        reason=reason,
        disputed_amount_paise=disputed_amount_paise,
        status="OPEN",
    )
    db.add(dispute)
    db.flush()
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "DISPUTE_OPENED",
        actor_user_id,
        payload={
            "dispute_id": dispute.dispute_code,
            "reason": reason,
            "disputed_amount_paise": disputed_amount_paise,
        },
        commit=False,
    )
    db.commit()
    db.refresh(dispute)
    return dispute


def add_evidence(
    db: Session,
    dispute: Dispute,
    actor_user_id: UUID,
    evidence_type: str,
    evidence_reference: str,
) -> DisputeEvidence:
    _require_open_dispute(dispute)
    row = DisputeEvidence(
        dispute_id=dispute.id,
        evidence_type=evidence_type,
        evidence_reference=evidence_reference,
    )
    db.add(row)
    db.flush()
    append_event(
        db,
        "TRANSACTION",
        dispute.transaction_id,
        "DISPUTE_EVIDENCE_ADDED",
        actor_user_id,
        payload={
            "dispute_id": dispute.dispute_code,
            "evidence_id": str(row.id),
            "evidence_type": evidence_type,
        },
        commit=False,
    )
    db.commit()
    db.refresh(row)
    return row


def attach_reweigh(
    db: Session,
    dispute: Dispute,
    actor_user_id: UUID,
    weighment_code: str,
    stage: str,
) -> DisputeReweigh:
    _require_open_dispute(dispute)
    ws = db.scalar(select(WeighmentSession).where(WeighmentSession.weighment_code == weighment_code))
    if not ws or ws.status != "VERIFIED":
        raise AppError("VERIFIED_REWEIGH_REQUIRED", "Verified reweigh session required.", 409)

    tx = db.get(Transaction, dispute.transaction_id)
    if tx is None:
        raise AppError("TRANSACTION_NOT_FOUND", "Transaction not found.", 404)
    listing = db.get(Listing, tx.listing_id)
    if listing is None:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    _assert_reweigh_matches_listing(ws, listing)

    row = DisputeReweigh(
        dispute_id=dispute.id,
        weighment_session_id=ws.id,
        stage=stage,
        status="RECORDED",
    )
    db.add(row)
    db.flush()
    append_event(
        db,
        "TRANSACTION",
        dispute.transaction_id,
        "DISPUTE_REWEIGH_ATTACHED",
        actor_user_id,
        payload={
            "dispute_id": dispute.dispute_code,
            "reweigh_id": str(row.id),
            "weighment_code": ws.weighment_code,
            "stage": stage,
        },
        commit=False,
    )
    db.commit()
    db.refresh(row)
    return row


def resolve_dispute(
    db: Session,
    tx: Transaction,
    dispute: Dispute,
    actor_user_id: UUID,
    final_decision: str,
    settlement_adjustment_paise: int,
    resolution_rule: str,
) -> Dispute:
    if dispute.status == "RESOLVED":
        return dispute

    dispute.final_decision = final_decision
    dispute.settlement_adjustment_paise = settlement_adjustment_paise
    dispute.resolution_rule = resolution_rule
    dispute.status = "RESOLVED"

    transition_transaction(db, tx, "RESOLVED", commit=False)
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "DISPUTE_RESOLVED",
        actor_user_id,
        payload={
            "dispute_id": dispute.dispute_code,
            "settlement_adjustment_paise": settlement_adjustment_paise,
            "resolution_rule": resolution_rule,
        },
        commit=False,
    )
    db.commit()
    db.refresh(tx)
    db.refresh(dispute)
    return dispute
