from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_farmer_kyc_verified
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.marketplace.models import Bid, Listing
from app.transaction.schemas import TransactionResponse
from app.transaction.service import create_transaction_from_accepted_bid, transaction_for_party

router = APIRouter(prefix="/transaction", tags=["transaction"])


def _require_farmer_listing_owner(db: Session, user_id: UUID, listing: Listing) -> FarmerProfile:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    if farmer is None or farmer.id != listing.seller_farmer_profile_id:
        raise AppError("FORBIDDEN", "Farmer does not own this listing.", 403)
    return farmer


@router.post("/from-listing/{listing_id}", response_model=TransactionResponse, status_code=201)
def create_from_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    listing = db.scalar(select(Listing).where(Listing.listing_code == listing_id))
    if not listing:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    _require_farmer_listing_owner(db, user.id, listing)
    if listing.status != "OFFER_ACCEPTED" or not listing.accepted_bid_id:
        raise AppError("OFFER_NOT_ACCEPTED", "Listing does not have an accepted bid.", 409)
    bid = db.get(Bid, listing.accepted_bid_id)
    if bid is None:
        raise AppError("BID_NOT_FOUND", "Accepted bid not found.", 404)
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
    if listing is None:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    if bid is None:
        raise AppError("BID_NOT_FOUND", "Accepted bid not found.", 404)
    return TransactionResponse(
        transaction_id=tx.transaction_code,
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        state=tx.state,
        active_agreement_id=str(tx.active_agreement_id) if tx.active_agreement_id else None,
    )
