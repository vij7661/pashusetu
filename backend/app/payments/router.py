from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.auth.dependencies import current_user, require_farmer_kyc_verified
from app.core.errors import AppError
from app.db.session import get_db
from app.disputes.models import Settlement
from app.identity.models import User
from app.marketplace.models import Bid
from app.payments.models import PaymentIntent
from app.payments.provider import SimulatedFundsProvider
from app.payments.schemas import SecureFundsResponse, SettlementResponse
from app.payments.settlement_service import create_settlement
from app.transaction.service import transaction_for_party, transition_transaction

router = APIRouter(prefix="/payments", tags=["payments"])


def _settlement_response(row: Settlement) -> SettlementResponse:
    return SettlementResponse(
        settlement_id=row.settlement_code,
        gross_amount_paise=row.gross_amount_paise,
        adjustment_paise=row.adjustment_paise,
        platform_fee_paise=row.platform_fee_paise,
        final_amount_paise=row.final_amount_paise,
        status=row.status,
    )


@router.post(
    "/transactions/{transaction_id}/secure",
    response_model=SecureFundsResponse,
)
def secure(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "AGREEMENT_LOCKED":
        raise AppError("FUNDS_SECURE_NOT_ALLOWED", "Agreement must be locked first.", 409)

    bid = db.get(Bid, tx.accepted_bid_id)
    if bid is None:
        raise AppError("ACCEPTED_BID_NOT_FOUND", "Accepted bid not found.", 500)

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
    db.flush()
    transition_transaction(db, tx, "FUNDS_SECURED", commit=False)
    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "FUNDS_SECURED",
        user.id,
        payload={
            "payment_intent_id": str(row.id),
            "provider": row.provider,
            "amount_paise": row.amount_paise,
        },
        commit=False,
    )
    db.commit()
    db.refresh(row)

    return SecureFundsResponse(
        payment_intent_id=str(row.id),
        provider_reference=payment.provider_reference,
        amount_paise=row.amount_paise,
        status=row.status,
        transaction_state=tx.state,
    )


@router.get(
    "/transactions/{transaction_id}/settlement",
    response_model=SettlementResponse,
)
def get_settlement(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    row = db.scalar(select(Settlement).where(Settlement.transaction_id == tx.id))
    if row is None:
        raise AppError("SETTLEMENT_NOT_FOUND", "Settlement has not been created yet.", 404)
    return _settlement_response(row)


@router.post(
    "/transactions/{transaction_id}/settle",
    response_model=SettlementResponse,
)
def settle_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    row = create_settlement(db, tx, user.id)
    return _settlement_response(row)
