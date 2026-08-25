from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.disputes.models import Dispute, Settlement
from app.marketplace.models import Bid
from app.transaction.models import Transaction
from app.transaction.service import transition_transaction
from app.audit.service import append_event


def create_settlement(
    db: Session,
    tx: Transaction,
    actor_user_id: UUID | None = None,
    platform_fee_basis_points: int = 150,
) -> Settlement:
    existing = db.scalar(select(Settlement).where(Settlement.transaction_id == tx.id))
    if existing:
        return existing

    if tx.state not in {"SETTLED", "RESOLVED"}:
        raise AppError("SETTLEMENT_NOT_ALLOWED", "Transaction is not ready for settlement.", 409)

    bid = db.get(Bid, tx.accepted_bid_id)
    gross = bid.total_offer_paise
    dispute = db.scalar(select(Dispute).where(Dispute.transaction_id == tx.id))
    adjustment = dispute.settlement_adjustment_paise if dispute else 0
    fee = max(0, int((gross + adjustment) * platform_fee_basis_points / 10_000))
    final = gross + adjustment - fee
    if final < 0:
        raise AppError("INVALID_FINAL_SETTLEMENT", "Final settlement cannot be negative.", 409)

    settlement = Settlement(
        settlement_code=f"STL-{uuid4().hex[:10].upper()}",
        transaction_id=tx.id,
        gross_amount_paise=gross,
        adjustment_paise=adjustment,
        platform_fee_paise=fee,
        final_amount_paise=final,
        status="COMPLETED",
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)

    if tx.state == "RESOLVED":
        transition_transaction(db, tx, "SETTLED")

    append_event(
        db, "TRANSACTION", tx.id, "SETTLEMENT_COMPLETED", actor_user_id,
        payload={
            "settlement_id": settlement.settlement_code,
            "gross_amount_paise": gross,
            "adjustment_paise": adjustment,
            "platform_fee_paise": fee,
            "final_amount_paise": final,
        },
    )
    return settlement
