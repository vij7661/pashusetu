from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.core.errors import AppError
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.marketplace.models import Bid, Listing
from app.transaction.models import Transaction
from app.transaction.state_machine import assert_transition


def create_transaction_from_accepted_bid(
    db: Session,
    listing: Listing,
    bid: Bid,
    actor_user_id: UUID | None = None,
    *,
    commit: bool = True,
) -> Transaction:
    existing = db.scalar(select(Transaction).where(Transaction.listing_id == listing.id))
    if existing:
        return existing

    transaction = Transaction(
        transaction_code=f"TX-{uuid4().hex[:10].upper()}",
        listing_id=listing.id,
        farmer_profile_id=listing.seller_farmer_profile_id,
        buyer_profile_id=bid.buyer_profile_id,
        accepted_bid_id=bid.id,
        state="OFFER_ACCEPTED",
    )
    db.add(transaction)
    db.flush()
    append_event(
        db,
        "TRANSACTION",
        transaction.id,
        "TRANSACTION_CREATED",
        actor_user_id,
        payload={
            "transaction_id": transaction.transaction_code,
            "listing_id": listing.listing_code,
            "accepted_bid_id": bid.bid_code,
        },
        commit=False,
    )
    if commit:
        db.commit()
        db.refresh(transaction)
    return transaction


def transaction_for_party(db: Session, transaction_code: str, user_id: UUID) -> Transaction:
    tx = db.scalar(select(Transaction).where(Transaction.transaction_code == transaction_code))
    if not tx:
        raise AppError("TRANSACTION_NOT_FOUND", "Transaction not found.", 404)

    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    if farmer and farmer.id == tx.farmer_profile_id:
        return tx

    buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user_id))
    if buyer and buyer.id == tx.buyer_profile_id:
        return tx

    raise AppError("FORBIDDEN", "User is not a party to this transaction.", 403)


def transition_transaction(
    db: Session,
    tx: Transaction,
    target_state: str,
    *,
    commit: bool = True,
) -> Transaction:
    assert_transition(tx.state, target_state)
    tx.state = target_state
    if commit:
        db.commit()
        db.refresh(tx)
    else:
        db.flush()
    return tx
