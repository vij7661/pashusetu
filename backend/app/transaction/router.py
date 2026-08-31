from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.reputation_service import close_transaction_reputation
from app.auth.dependencies import current_user, require_farmer_kyc_verified
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.marketplace.models import Bid, Listing
from app.transaction.schemas import TransactionResponse
from app.transaction.service import (
    create_transaction_from_accepted_bid,
    transaction_for_party,
    transition_transaction,
)

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/from-listing/{listing_id}", response_model=TransactionResponse, status_code=201)
def create_from_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    listing = db.scalar(select(Listing).where(Listing.listing_code == listing_id))
    if not listing:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    if listing.status != "OFFER_ACCEPTED" or not listing.accepted_bid_id:
        raise AppError("OFFER_NOT_ACCEPTED", "Listing does not have an accepted bid.", 409)
    bid = db.get(Bid, listing.accepted_bid_id)
    tx = create_transaction_from_accepted_bid(db, listing, bid)
    tx = transaction_for_party(db, tx.transaction_code, user.id)
    return TransactionResponse(
        transaction_id=tx.transaction_code,
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        state=tx.state,
        active_agreement_id=str(tx.active_agreement_id) if tx.active_agreement_id else None,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    listing = db.get(Listing, tx.listing_id)
    bid = db.get(Bid, tx.accepted_bid_id)
    return TransactionResponse(
        transaction_id=tx.transaction_code,
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        state=tx.state,
        active_agreement_id=str(tx.active_agreement_id) if tx.active_agreement_id else None,
    )


@router.post("/{transaction_id}/close", response_model=TransactionResponse)
def close_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if tx.state != "SETTLED":
        raise AppError(
            "TRANSACTION_NOT_SETTLED",
            "Only settled transactions may be closed.",
            409,
        )
    transition_transaction(db, tx, "CLOSED")
    close_transaction_reputation(db, tx)
    listing = db.get(Listing, tx.listing_id)
    bid = db.get(Bid, tx.accepted_bid_id)
    return TransactionResponse(
        transaction_id=tx.transaction_code,
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        state=tx.state,
        active_agreement_id=str(tx.active_agreement_id) if tx.active_agreement_id else None,
    )
