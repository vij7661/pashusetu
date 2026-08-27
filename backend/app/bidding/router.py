from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.bidding.schemas import BidAcceptanceResponse, BidCreate, BidResponse
from app.bidding.service import accept_bid, submit_bid
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.marketplace.models import Bid, Listing
from app.transaction.service import create_transaction_from_accepted_bid

router = APIRouter(prefix="/bidding", tags=["bidding"])


@router.post("/listings/{listing_id}/bids", response_model=BidResponse, status_code=201)
def post_bid(
    listing_id: str,
    payload: BidCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    bid = submit_bid(
        db,
        user.id,
        listing_id,
        payload.price_per_kg_paise,
        idempotency_key,
    )
    listing = db.get(Listing, bid.listing_id)
    return BidResponse(
        bid_id=bid.bid_code,
        listing_id=listing.listing_code,
        price_per_kg_paise=bid.price_per_kg_paise,
        total_offer_paise=bid.total_offer_paise,
        server_sequence=bid.server_sequence,
        status=bid.status,
        reject_reason=bid.reject_reason,
    )


@router.get("/listings/{listing_id}/bids", response_model=list[BidResponse])
def list_bids(
    listing_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    listing = db.scalar(select(Listing).where(Listing.listing_code == listing_id))
    if not listing:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user.id))
    if farmer and listing.seller_farmer_profile_id == farmer.id:
        bid_filter = Bid.listing_id == listing.id
    elif buyer:
        bid_filter = (Bid.listing_id == listing.id) & (Bid.buyer_profile_id == buyer.id)
    else:
        raise AppError("FORBIDDEN", "Only the seller or bidding Buyer may review offers.", 403)
    rows = db.scalars(
        select(Bid)
        .where(bid_filter)
        .order_by(Bid.price_per_kg_paise.desc(), Bid.server_sequence.asc())
    ).all()
    return [
        BidResponse(
            bid_id=x.bid_code,
            listing_id=listing.listing_code,
            price_per_kg_paise=x.price_per_kg_paise,
            total_offer_paise=x.total_offer_paise,
            server_sequence=x.server_sequence,
            status=x.status,
            reject_reason=x.reject_reason,
        )
        for x in rows
    ]


@router.post("/listings/{listing_id}/accept/{bid_id}", response_model=BidAcceptanceResponse)
def post_accept_bid(
    listing_id: str,
    bid_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    listing, bid = accept_bid(db, user.id, listing_id, bid_id)
    create_transaction_from_accepted_bid(db, listing, bid)
    return BidAcceptanceResponse(
        listing_id=listing.listing_code,
        accepted_bid_id=bid.bid_code,
        accepted_server_sequence=bid.server_sequence,
        status=listing.status,
    )
