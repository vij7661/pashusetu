from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.reputation_service import close_transaction_reputation
from app.auth.dependencies import current_user, require_farmer_kyc_verified
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.marketplace.models import Bid, Listing
from app.transaction.models import Transaction
from app.transaction.schemas import TransactionResponse
from app.transaction.service import (
    create_transaction_from_accepted_bid,
    transaction_for_party,
    transition_transaction,
)

router = APIRouter(prefix="/transaction", tags=["transaction"])


def _response(db: Session, tx: Transaction) -> TransactionResponse:
    listing = db.get(Listing, tx.listing_id)
    bid = db.get(Bid, tx.accepted_bid_id)
    if listing is None or bid is None:
        raise AppError(
            "TRANSACTION_STATE_INVALID",
            "Transaction listing or accepted bid is missing.",
            500,
        )
    return TransactionResponse(
        transaction_id=tx.transaction_code,
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        state=tx.state,
        active_agreement_id=(
            str(tx.active_agreement_id) if tx.active_agreement_id else None
        ),
    )


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
    return _response(db, tx)


@router.get("/mine", response_model=list[TransactionResponse])
def get_my_transactions(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if farmer is None:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 409)
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.farmer_profile_id == farmer.id)
        .order_by(Transaction.created_at.desc())
    ).all()
    return [_response(db, tx) for tx in rows]


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    return _response(db, tx)


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
    return _response(db, tx)
