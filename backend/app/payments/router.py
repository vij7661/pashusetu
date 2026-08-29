from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_farmer_kyc_verified
from app.db.session import get_db
from app.identity.models import User
from app.marketplace.models import Bid
from app.payments.models import PaymentIntent
from app.payments.provider import SimulatedFundsProvider
from app.payments.settlement_service import create_settlement
from app.transaction.service import transaction_for_party, transition_transaction

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/transactions/{transaction_id}/secure")
def secure(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "AGREEMENT_LOCKED":
        return {"status": tx.state, "detail": "Agreement must be locked first."}
    bid = db.get(Bid, tx.accepted_bid_id)
    payment = SimulatedFundsProvider().create_secure_funds_intent(
        tx.transaction_code,
        bid.total_offer_paise,
    )
    row = PaymentIntent(
        transaction_id=tx.id,
        provider="SIMULATED",
        provider_reference=payment.provider_reference,
        amount_paise=bid.total_offer_paise,
        status="SECURED",
    )
    db.add(row)
    db.commit()
    transition_transaction(db, tx, "FUNDS_SECURED")
    return {
        "payment_intent_id": str(row.id),
        "provider_reference": payment.provider_reference,
        "amount_paise": row.amount_paise,
        "status": row.status,
        "transaction_state": tx.state,
    }


@router.post("/transactions/{transaction_id}/settle")
def settle_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    row = create_settlement(db, tx, user.id)
    return {
        "settlement_id": row.settlement_code,
        "gross_amount_paise": row.gross_amount_paise,
        "adjustment_paise": row.adjustment_paise,
        "platform_fee_paise": row.platform_fee_paise,
        "final_amount_paise": row.final_amount_paise,
        "status": row.status,
    }
