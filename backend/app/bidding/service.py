import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.marketplace.models import Bid, BidSequence, IdempotencyRecord, Listing
from app.marketplace.service import calculate_total_paise


def _buyer_for_user(db: Session, user_id: UUID) -> BuyerProfile:
    buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user_id))
    if not buyer:
        raise AppError("BUYER_PROFILE_REQUIRED", "Buyer profile is required.", 409)
    return buyer


def _fingerprint(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def submit_bid(
    db: Session,
    user_id: UUID,
    listing_code: str,
    price_per_kg_paise: int,
    idempotency_key: str,
) -> Bid:
    buyer = _buyer_for_user(db, user_id)
    request_fp = _fingerprint({
        "listing_code": listing_code,
        "price_per_kg_paise": price_per_kg_paise,
    })

    existing_idem = db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.actor_user_id == user_id,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
    )
    if existing_idem:
        if existing_idem.request_fingerprint != request_fp:
            raise AppError(
                "IDEMPOTENCY_KEY_REUSED",
                "Idempotency key was reused with a different bid request.",
                409,
            )
        if existing_idem.resource_type == "BID" and existing_idem.resource_id:
            existing_bid = db.get(Bid, existing_idem.resource_id)
            if existing_bid:
                return existing_bid

    listing = db.scalar(
        select(Listing).where(Listing.listing_code == listing_code).with_for_update()
    )
    if not listing:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)

    now = datetime.now(timezone.utc)
    if listing.status != "PUBLISHED":
        raise AppError("LISTING_NOT_OPEN", "Listing is not open for bidding.", 409)
    if now < listing.opens_at:
        raise AppError("LISTING_NOT_OPEN", "Listing has not opened yet.", 409)
    if now >= listing.closes_at:
        listing.status = "CLOSED"
        db.commit()
        raise AppError("LISTING_CLOSED", "Listing is closed.", 409)

    seq = db.scalar(
        select(BidSequence).where(BidSequence.listing_id == listing.id).with_for_update()
    )
    if not seq:
        seq = BidSequence(listing_id=listing.id, last_sequence=0)
        db.add(seq)
        db.flush()
    seq.last_sequence += 1

    bid = Bid(
        bid_code=f"BID-{uuid4().hex[:10].upper()}",
        listing_id=listing.id,
        buyer_profile_id=buyer.id,
        price_per_kg_paise=price_per_kg_paise,
        total_offer_paise=calculate_total_paise(listing.verified_weight_kg, price_per_kg_paise),
        idempotency_key=idempotency_key,
        server_sequence=seq.last_sequence,
        status="ACTIVE",
    )
    db.add(bid)
    db.flush()

    db.add(
        IdempotencyRecord(
            actor_user_id=user_id,
            idempotency_key=idempotency_key,
            operation="SUBMIT_BID",
            request_fingerprint=request_fp,
            resource_type="BID",
            resource_id=bid.id,
            response_status=201,
        )
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Bid).where(
                Bid.listing_id == listing.id,
                Bid.buyer_profile_id == buyer.id,
                Bid.idempotency_key == idempotency_key,
            )
        )
        if existing:
            return existing
        raise
    db.refresh(bid)
    return bid


def accept_bid(
    db: Session,
    farmer_user_id: UUID,
    listing_code: str,
    bid_code: str,
) -> tuple[Listing, Bid]:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == farmer_user_id))
    if not farmer:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 409)

    listing = db.scalar(
        select(Listing).where(Listing.listing_code == listing_code).with_for_update()
    )
    if not listing:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    if listing.seller_farmer_profile_id != farmer.id:
        raise AppError("FORBIDDEN", "Farmer does not own this listing.", 403)

    if listing.accepted_bid_id:
        accepted = db.get(Bid, listing.accepted_bid_id)
        return listing, accepted

    if listing.status not in {"PUBLISHED", "CLOSED"}:
        raise AppError("LISTING_NOT_ACCEPTABLE", "Listing cannot accept a bid in its current state.", 409)

    bid = db.scalar(
        select(Bid).where(
            Bid.bid_code == bid_code,
            Bid.listing_id == listing.id,
            Bid.status == "ACTIVE",
        )
    )
    if not bid:
        raise AppError("BID_NOT_VALID", "Bid is not active/valid for this listing.", 404)

    # Deterministic rule for equal-price offers: earliest server sequence wins among equal amounts.
    best = db.scalar(
        select(Bid)
        .where(Bid.listing_id == listing.id, Bid.status == "ACTIVE")
        .order_by(Bid.price_per_kg_paise.desc(), Bid.server_sequence.asc())
    )
    if best and best.id != bid.id:
        raise AppError(
            "BID_NOT_CURRENT_PRIORITY",
            "Selected bid is not the current highest-priority valid offer.",
            409,
        )

    listing.accepted_bid_id = bid.id
    listing.status = "OFFER_ACCEPTED"
    bid.status = "ACCEPTED"

    other_bids = db.scalars(
        select(Bid).where(Bid.listing_id == listing.id, Bid.id != bid.id, Bid.status == "ACTIVE")
    ).all()
    for other in other_bids:
        other.status = "NOT_SELECTED"

    db.commit()
    db.refresh(listing)
    db.refresh(bid)
    return listing, bid
