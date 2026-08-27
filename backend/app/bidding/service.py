import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit.domain_events import listing_event
from app.core.errors import AppError
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.marketplace.models import Bid, BidSequence, IdempotencyRecord, Listing
from app.marketplace.service import available_goats, calculate_total_paise, trusted_goat_weights


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
    selected_goat_codes: list[str],
    whole_lot: bool,
) -> Bid:
    buyer = _buyer_for_user(db, user_id)
    request_fp = _fingerprint(
        {
            "listing_code": listing_code,
            "price_per_kg_paise": price_per_kg_paise,
            "selected_goat_ids": sorted(selected_goat_codes),
            "whole_lot": whole_lot,
        }
    )

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

    now = datetime.now(UTC)
    if listing.status != "PUBLISHED":
        raise AppError("LISTING_NOT_OPEN", "Listing is not open for bidding.", 409)
    if now < listing.opens_at:
        raise AppError("LISTING_NOT_OPEN", "Listing has not opened yet.", 409)
    if now >= listing.closes_at:
        listing.status = "CLOSED"
        db.commit()
        raise AppError("LISTING_CLOSED", "Listing is closed.", 409)

    available, complete = available_goats(db, listing)
    available_by_code = {goat.goat_code: goat for goat in available}
    if listing.target_type == "GOAT":
        selected = available
        whole_lot = True
    elif whole_lot:
        selected = available
    else:
        if len(selected_goat_codes) < 3:
            raise AppError(
                "MINIMUM_PARTIAL_QUANTITY", "A partial lot bid requires at least 3 goats.", 400
            )
        if len(set(selected_goat_codes)) != len(selected_goat_codes) or any(
            code not in available_by_code for code in selected_goat_codes
        ):
            raise AppError(
                "GOAT_SELECTION_UNAVAILABLE", "Selected goats are not all available.", 409
            )
        if not complete:
            raise AppError(
                "LOT_IDENTITY_INCOMPLETE",
                "Every declared goat must be individually identified.",
                409,
            )
        selected = [available_by_code[code] for code in selected_goat_codes]
    if listing.target_type == "LOT" and len(selected) < 3:
        raise AppError("MINIMUM_QUANTITY_REQUIRED", "Minimum lot purchase is 3 goats.", 400)
    if listing.target_type == "LOT" and not whole_lot:
        weights = trusted_goat_weights(db, selected)
        if len(weights) != len(selected):
            raise AppError(
                "TRUSTED_GOAT_WEIGHTS_REQUIRED",
                "Partial bids require verified weight for every selected goat.",
                409,
            )
        commercial_weight = sum(weights.values(), Decimal(0))
    else:
        commercial_weight = listing.verified_weight_kg

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
        total_offer_paise=calculate_total_paise(commercial_weight, price_per_kg_paise),
        idempotency_key=idempotency_key,
        server_sequence=seq.last_sequence,
        status="ACTIVE",
        selected_goat_ids=[goat.id for goat in selected],
        selected_quantity=len(selected),
        selected_weight_kg=commercial_weight,
        whole_lot=whole_lot,
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
        listing_event(
            db,
            listing.id,
            "BID_SUBMITTED",
            actor_user_id=user_id,
            payload={"bid_code": bid.bid_code, "server_sequence": bid.server_sequence},
        )
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

    already_accepted = db.scalar(
        select(Bid).where(
            Bid.listing_id == listing.id,
            Bid.bid_code == bid_code,
            Bid.status == "ACCEPTED",
        )
    )
    if already_accepted:
        return listing, already_accepted

    if listing.status not in {"PUBLISHED", "CLOSED"}:
        raise AppError(
            "LISTING_NOT_ACCEPTABLE", "Listing cannot accept a bid in its current state.", 409
        )

    bid = db.scalar(
        select(Bid).where(
            Bid.bid_code == bid_code,
            Bid.listing_id == listing.id,
            Bid.status == "ACTIVE",
        )
    )
    if not bid:
        raise AppError("BID_NOT_VALID", "Bid is not active/valid for this listing.", 404)

    accepted_bids = db.scalars(
        select(Bid).where(Bid.listing_id == listing.id, Bid.status == "ACCEPTED")
    ).all()
    if any(accepted_bid.whole_lot for accepted_bid in accepted_bids) or (
        bid.whole_lot and accepted_bids
    ):
        raise AppError(
            "GOAT_SELECTION_ALREADY_ACCEPTED",
            "The whole lot or part of it has already been accepted.",
            409,
        )
    sold_ids = {
        goat_id for accepted_bid in accepted_bids for goat_id in accepted_bid.selected_goat_ids
    }
    if sold_ids.intersection(bid.selected_goat_ids):
        raise AppError(
            "GOAT_SELECTION_ALREADY_ACCEPTED",
            "One or more selected goats are no longer available.",
            409,
        )

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
        if set(other.selected_goat_ids).intersection(bid.selected_goat_ids):
            other.status = "NOT_SELECTED"

    remaining, _ = available_goats(db, listing)
    remaining_ids = {goat.id for goat in remaining} - set(bid.selected_goat_ids)
    listing.status = "PUBLISHED" if len(remaining_ids) >= 3 else "OFFER_ACCEPTED"

    listing_event(
        db,
        listing.id,
        "BID_ACCEPTED",
        actor_user_id=farmer_user_id,
        payload={"bid_code": bid.bid_code, "server_sequence": bid.server_sequence},
    )
    db.refresh(listing)
    db.refresh(bid)
    return listing, bid
